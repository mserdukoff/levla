# Host Levla on AWS

Step-by-step production deploy: **ECS Fargate**, an **Application Load Balancer**, **RDS Postgres 16**, **S3** for audio, and **Secrets Manager**. Task definition templates live in [`infra/aws/`](../infra/aws/).

If you only want a cheap staging box first, skip to [Option B: one EC2 instance](#option-b-one-ec2-instance).

---

## What you are building

```
Internet
   │
   ▼
ALB  (HTTPS, idle timeout 120s)
   ├─ /api/*  →  ECS service: backend  :8000
   └─ /*      →  ECS service: frontend :3000

Private subnets
   ├─ ECS: backend  (FastAPI + optional gen threads)
   ├─ ECS: frontend (Next.js standalone)
   ├─ ECS: worker   (generation jobs only)
   ├─ RDS Postgres 16
   └─ S3  (passage MP3s)

Secrets Manager  →  DATABASE_URL, JWT_SECRET, API keys
ECR              →  levla-backend, levla-frontend
```

Browser `/api` calls go straight to FastAPI. The Next.js server still talks to the backend on the **private** network (`NLP_BACKEND_URL`) for SSR passage pages.

Generation is async: `POST /api/generate` returns a job id; worker tasks claim rows from Postgres. Reads stay fast while generations run.

---

## Before you start

You need:

- An AWS account and the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) (`aws configure`)
- Docker
- A domain name you can point at an ALB (or skip TLS and use the ALB DNS name for a first test)
- An [OpenRouter](https://openrouter.ai/) API key (generation, gloss fill, translation)
- Optional: Google OAuth client, Azure Speech key

Pick a region and stick to it. Examples below use `us-east-1`.

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export DOMAIN=read.example.com          # your public hostname
```

Expect a first-month bill in the **tens of dollars** for a small Fargate + RDS setup if you leave it running. Fargate + ALB + RDS do not have a meaningful free tier.

---

## Step 1 — Networking

Use a VPC with **two public subnets** (ALB) and **two private subnets** (ECS + RDS) across two AZs. Private subnets need a NAT gateway so tasks can reach OpenRouter, ECR, S3, and Azure.

Easiest path: [VPC wizard](https://console.aws.amazon.com/vpc/home#CreateVpc:createMode=vpcFromTemplate) → **VPC and more** → 2 AZs, public + private subnets, 1 NAT gateway.

Note these IDs:

```bash
export VPC_ID=vpc-xxxxxxxx
export PUBLIC_SUBNET_1=subnet-aaaa
export PUBLIC_SUBNET_2=subnet-bbbb
export PRIVATE_SUBNET_1=subnet-cccc
export PRIVATE_SUBNET_2=subnet-dddd
```

### Security groups

```bash
# ALB: 80/443 from the internet
aws ec2 create-security-group --group-name levla-alb --description "Levla ALB" --vpc-id "$VPC_ID"
export ALB_SG=sg-alb

aws ec2 authorize-security-group-ingress --group-id "$ALB_SG" --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id "$ALB_SG" --protocol tcp --port 443 --cidr 0.0.0.0/0

# Frontend: 3000 from ALB
aws ec2 create-security-group --group-name levla-frontend --description "Levla frontend" --vpc-id "$VPC_ID"
export FE_SG=sg-frontend
aws ec2 authorize-security-group-ingress --group-id "$FE_SG" --protocol tcp --port 3000 --source-group "$ALB_SG"

# Backend: 8000 from ALB (public /api) and from frontend (SSR)
aws ec2 create-security-group --group-name levla-backend --description "Levla backend" --vpc-id "$VPC_ID"
export BE_SG=sg-backend
aws ec2 authorize-security-group-ingress --group-id "$BE_SG" --protocol tcp --port 8000 --source-group "$ALB_SG"
aws ec2 authorize-security-group-ingress --group-id "$BE_SG" --protocol tcp --port 8000 --source-group "$FE_SG"

# Worker: no inbound. Same outbound as backend (RDS, S3, OpenRouter).
aws ec2 create-security-group --group-name levla-worker --description "Levla worker" --vpc-id "$VPC_ID"
export WK_SG=sg-worker

# RDS: 5432 from backend and worker only
aws ec2 create-security-group --group-name levla-rds --description "Levla RDS" --vpc-id "$VPC_ID"
export RDS_SG=sg-rds
aws ec2 authorize-security-group-ingress --group-id "$RDS_SG" --protocol tcp --port 5432 --source-group "$BE_SG"
aws ec2 authorize-security-group-ingress --group-id "$RDS_SG" --protocol tcp --port 5432 --source-group "$WK_SG"
```

Replace `sg-alb` etc. with the IDs the create commands print.

---

## Step 2 — RDS Postgres 16

1. Create a DB subnet group on the **private** subnets.
2. Create a Postgres 16 instance:
   - Engine: PostgreSQL 16
   - Instance: `db.t4g.micro` is enough to start
   - Storage: 20 GB gp3
   - Not publicly accessible
   - VPC security group: `levla-rds`
   - Database name: `levla`
   - Username: `levla`
   - Strong password

Wait until the instance is **Available**. Copy the endpoint, e.g. `levla.xxxx.us-east-1.rds.amazonaws.com`.

URL shape (the app rewrites `postgres://` to `postgresql+psycopg2://`):

```
postgresql://levla:YOUR_PASSWORD@levla.xxxx.us-east-1.rds.amazonaws.com:5432/levla
```

Do **not** create tables by hand. The first backend task runs `init_db()` (create tables + seed library/catalog). That first boot can take several minutes.

---

## Step 3 — S3 for audio

Without a shared bucket, MP3s live on the container disk and disappear on every deploy.

```bash
export AUDIO_BUCKET=levla-audio-${AWS_ACCOUNT_ID}
aws s3 mb "s3://${AUDIO_BUCKET}" --region "$AWS_REGION"

# Block public access (API streams files; the bucket stays private)
aws s3api put-public-access-block --bucket "$AUDIO_BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

---

## Step 4 — Secrets Manager

Create one JSON secret. Do not put these values in the image or in git.

```bash
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")

aws secretsmanager create-secret --name levla/prod --secret-string "$(cat <<EOF
{
  "DATABASE_URL": "postgresql://levla:YOUR_PASSWORD@RDS_HOST:5432/levla",
  "JWT_SECRET": "${JWT_SECRET}",
  "OPENROUTER_API_KEY": "sk-or-...",
  "GOOGLE_CLIENT_SECRET": "",
  "AZURE_SPEECH_KEY": ""
}
EOF
)"
```

Copy the secret ARN (`arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:levla/prod-xxxxxx`). ECS injects keys with `ARN:KEY::` (see the task definitions).

---

## Step 5 — ECR

```bash
aws ecr create-repository --repository-name levla-backend
aws ecr create-repository --repository-name levla-frontend

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
```

From the **repo root**:

```bash
export TAG=$(git rev-parse --short HEAD)

docker build -f backend/Dockerfile -t levla-backend .
docker build -t levla-frontend ./frontend

docker tag levla-backend "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-backend:${TAG}"
docker tag levla-frontend "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-frontend:${TAG}"
docker tag levla-backend "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-backend:latest"
docker tag levla-frontend "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-frontend:latest"

docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-backend:${TAG}"
docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-frontend:${TAG}"
docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-backend:latest"
docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/levla-frontend:latest"
```

The backend image includes `data/` (lexicons). The frontend image is a Next.js standalone server; `NLP_BACKEND_URL` is read at **runtime**, so you do not rebuild when the internal backend hostname changes.

---

## Step 6 — IAM roles

Two roles:

| Role | Used by | Needs |
| ---- | ------- | ----- |
| **Execution role** | ECS agent | Pull from ECR, write CloudWatch logs, read Secrets Manager |
| **Task role** | Your process | S3 Get/Put/Head on the audio bucket |

### Execution role

Create `levla-ecs-execution` and attach:

- `AmazonECSTaskExecutionRolePolicy`
- An inline policy allowing `secretsmanager:GetSecretValue` on `levla/prod`

### Task role

Create `levla-ecs-task` with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:HeadObject"],
      "Resource": "arn:aws:s3:::YOUR_AUDIO_BUCKET/audio/*"
    }
  ]
}
```

Copy both role ARNs.

---

## Step 7 — CloudWatch log groups

```bash
aws logs create-log-group --log-group-name /ecs/levla-backend
aws logs create-log-group --log-group-name /ecs/levla-frontend
aws logs create-log-group --log-group-name /ecs/levla-worker
```

---

## Step 8 — Fill in the task definitions

Edit the three files in `infra/aws/`:

| File | Service |
| ---- | ------- |
| [`backend-task-definition.json`](../infra/aws/backend-task-definition.json) | HTTP API |
| [`frontend-task-definition.json`](../infra/aws/frontend-task-definition.json) | Next.js |
| [`worker-task-definition.json`](../infra/aws/worker-task-definition.json) | Generation workers |

Replace:

- `ARN_EXECUTION_ROLE` / `ARN_TASK_ROLE`
- `ACCOUNT`, `REGION`, `TAG`
- `https://YOUR_DOMAIN`
- `YOUR_AUDIO_BUCKET`
- `ARN_SECRET:DATABASE_URL::` → `arn:...:secret:levla/prod-xxxxxx:DATABASE_URL::` (same for the other keys)

Frontend `NLP_BACKEND_URL` must be the **internal** backend name. After you enable Service Connect (step 11) it is:

```
http://backend:8000
```

Register:

```bash
aws ecs register-task-definition --cli-input-json file://infra/aws/backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://infra/aws/frontend-task-definition.json
aws ecs register-task-definition --cli-input-json file://infra/aws/worker-task-definition.json
```

The worker JSON overrides Docker `ENTRYPOINT` (`python -m app.worker`). Do not run the default backend entrypoint on worker tasks — that would start uvicorn instead of the queue consumer.

---

## Step 9 — ACM certificate and ALB

### Certificate

In ACM (same region as the ALB), request a public cert for `$DOMAIN`. Validate with DNS.

```bash
export CERT_ARN=arn:aws:acm:us-east-1:ACCOUNT:certificate/xxxx
```

### Load balancer

1. Create an **internet-facing** ALB in the **public** subnets, security group `levla-alb`.
2. **Attributes → Idle timeout = 120 seconds** (translation and other long calls; generation itself is async).
3. Two target groups, both IP type (Fargate), HTTP:

| Target group | Port | Health check |
| ------------ | ---- | ------------ |
| `levla-frontend` | 3000 | `GET /health` |
| `levla-backend` | 8000 | `GET /health` |

Health checks hit the **container**, not the other service. Backend also exposes `GET /api/health/ready` (database). Use `/health` for the ALB so a slow first seed does not fail the load balancer; ECS `startPeriod` is already 300s on the backend.

4. HTTPS listener (443) with the ACM cert. Rules:

| Priority | Condition | Forward to |
| -------- | --------- | ---------- |
| 10 | Path `/api/*` | `levla-backend` |
| default | (everything else) | `levla-frontend` |

5. HTTP listener (80): redirect to HTTPS.

Copy the ALB DNS name (`levla-xxxxx.us-east-1.elb.amazonaws.com`).

---

## Step 10 — ECS cluster

```bash
aws ecs create-cluster --cluster-name levla
```

Create a [Service Connect](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html) (or Cloud Map) namespace, e.g. `levla.local`, so frontend SSR can reach `http://backend:8000`.

---

## Step 11 — Services (order matters)

Create all three as Fargate services in the **private** subnets.

### 11a. Backend first, desired count 1

- Task definition: `levla-backend`
- Security group: `levla-backend`
- Load balancer: container `backend`, port 8000, target group `levla-backend`
- Service Connect: port name `backend`, discovery name `backend`, port 8000
- Desired count: **1**

Watch logs until you see something like `Levla backend ready`. First boot seeds the library and Japanese catalog. That can take several minutes. Do not scale the API until seed finishes.

Confirm RDS has rows:

```bash
# From any host that can reach RDS, or ECS Exec:
# SELECT COUNT(*) FROM passages;
```

### 11b. Frontend

- Task definition: `levla-frontend`
- Security group: `levla-frontend`
- Load balancer: container `frontend`, port 3000, target group `levla-frontend`
- Service Connect client in `levla.local`
- Desired count: 1 (or 2)

`NLP_BACKEND_URL=http://backend:8000` must resolve via Service Connect.

### 11c. Worker

- Task definition: `levla-worker`
- Security group: `levla-worker`
- **No load balancer**
- `SKIP_SEED=true` (already in the template)
- Desired count: 1 to start; scale this to add generation capacity

### Extra API tasks later

If you scale the backend service above 1, set `SKIP_SEED=true` on those extra tasks (or keep seed on; already-calibrated rows are left alone, but first-boot analysis is slow). Easiest: one “bootstrap” revision with seed, then a later revision with `SKIP_SEED=true` for all API tasks.

---

## Step 12 — DNS

Create an A/AAAA **alias** from `$DOMAIN` to the ALB.

Google sign-in (if you use it): authorized redirect URI is:

```
https://YOUR_DOMAIN/api/auth/google/callback
```

Set `GOOGLE_CLIENT_ID` on the backend task environment and `GOOGLE_CLIENT_SECRET` in the secret. `PUBLIC_BASE_URL` must be `https://YOUR_DOMAIN`.

---

## Step 13 — Verify

```bash
# Frontend
curl -fsS "https://${DOMAIN}/health"
# {"ok":true,"name":"levla"}

# Backend through the ALB path rule
curl -fsS "https://${DOMAIN}/api/health"
curl -fsS "https://${DOMAIN}/api/health/ready"
# ready includes "db": true

# Shelf (needs a device id header for learner state; anonymous still returns a library)
curl -fsS "https://${DOMAIN}/api/library?language=ja"
```

Then in a browser:

1. Open `https://$DOMAIN` — landing page.
2. Open `/library` — Japanese shelf with seeded texts.
3. Open a passage — tokens and gloss load.
4. Restock (if `OPENROUTER_API_KEY` is set) — form stays on the progress UI; `POST /api/generate` returns **202**; the client polls `/api/generate/{job_id}` until the passage exists.

If generate returns 202 forever: worker logs (`/ecs/levla-worker`) and `SELECT * FROM generation_jobs ORDER BY created_at DESC LIMIT 5`.

---

## Environment reference

Backend (also see `backend/.env.example`):

| Variable | Production value |
| -------- | ---------------- |
| `APP_ENV` | `production` (refuses default `JWT_SECRET`; Secure cookies) |
| `JWT_SECRET` | Long random string (secret) |
| `DATABASE_URL` | RDS URL (secret) |
| `DB_SSLMODE` | `require` |
| `PUBLIC_BASE_URL` | `https://YOUR_DOMAIN` |
| `CORS_ORIGINS` | Optional extras; `PUBLIC_BASE_URL` is always added |
| `S3_AUDIO_BUCKET` | Audio bucket name |
| `AWS_REGION` | Same as the bucket |
| `OPENROUTER_API_KEY` | Required for generate / LLM gloss / translation |
| `WEB_CONCURRENCY` | Uvicorn processes (template: `2`) |
| `GENERATE_WORKERS` | Job threads per process (API template: `2`; worker template: `4`) |
| `GENERATE_MAX_PENDING` | Queued jobs per device/user (default `3`) |
| `SKIP_SEED` | `true` on workers and extra API tasks |

Frontend:

| Variable | Production value |
| -------- | ---------------- |
| `NLP_BACKEND_URL` | Internal backend, e.g. `http://backend:8000` |

---

## Scaling generation

Concurrent generations ≈ **(worker tasks) × (GENERATE_WORKERS)**.

| Knob | What it does |
| ---- | ------------ |
| Worker **desired count** | Horizontal scale. Jobs are claimed with `FOR UPDATE SKIP LOCKED`. |
| `GENERATE_WORKERS` | Threads per container. Raise with vCPU; analysis is CPU-heavy. |
| `WEB_CONCURRENCY` | HTTP capacity for reads, not LLM work. |
| OpenRouter limits | Real ceiling once AWS capacity is high enough. |

Example: 5 worker tasks × 8 threads ≈ 40 concurrent generations, while API tasks keep serving the shelf.

Autoscaling idea: CloudWatch metric on `COUNT(*) FROM generation_jobs WHERE status = 'pending'`, scale the worker service on queue depth.

To push generation entirely off the API boxes, set `GENERATE_WORKERS=0` on the backend task definition and run only the worker service for jobs.

---

## Updating the app

1. Build and push new images with a new `TAG`.
2. Update the image field in the task definition JSON (or `aws ecs register-task-definition`).
3. `aws ecs update-service --cluster levla --service levla-backend --force-new-deployment` (same for frontend and worker).

Do not bake `.env` into the image. Change secrets in Secrets Manager, then bounce the services if they cache env at start (they read env at process start).

---

## Troubleshooting

| Symptom | Likely cause |
| ------- | ------------ |
| Backend never healthy | Seed still running; wait, or check `/ecs/levla-backend`. `startPeriod` must be 300s. |
| `JWT_SECRET must be a long random value` | `APP_ENV=production` with `dev-change-me`. |
| Frontend 502 on `/api/*` | ALB `/api/*` rule missing, or backend target group unhealthy. |
| Shelf loads, passages 502 on first paint | `NLP_BACKEND_URL` does not resolve inside the frontend task (Service Connect). |
| Generate 202, never completes | Worker not running, or still using uvicorn entrypoint. Confirm `python -m app.worker` in logs. |
| Audio works once, gone after deploy | `S3_AUDIO_BUCKET` unset. |
| RDS connection timeout | Backend/worker SG not allowed on RDS SG, or tasks in public subnets without a route. |
| Google redirect mismatch | Callback must be `https://DOMAIN/api/auth/google/callback` and ALB must send `/api/*` to FastAPI. |

---

## Option B: one EC2 instance

Valid for staging. Cheaper, not multi-AZ.

1. Create RDS as in step 2 (or run Postgres on the box; RDS is still better).
2. Launch Amazon Linux 2023 in a public subnet, Docker + Docker Compose installed.
3. Copy the repo (or pull images from ECR).
4. `backend/.env` with `APP_ENV=production`, real `JWT_SECRET`, `DATABASE_URL` pointing at RDS, `PUBLIC_BASE_URL=https://$DOMAIN`, `DB_SSLMODE=require`.
5. `docker compose up -d --build`
6. Put Caddy or nginx on the host (or an ALB) for TLS. Proxy `/` to `:3000` and `/api` to `:8000`.

Move to Fargate when you want frontend, API, and workers to scale independently.

---

## Checklist

- [ ] VPC: public + private subnets, NAT
- [ ] Security groups: ALB → frontend/backend; backend+worker → RDS
- [ ] RDS Postgres 16, not public
- [ ] S3 audio bucket, private
- [ ] Secrets Manager filled
- [ ] Images in ECR
- [ ] Execution + task IAM roles
- [ ] ACM cert, ALB idle 120s, `/api/*` → backend
- [ ] ECS: backend count 1 until seed finishes
- [ ] Frontend `NLP_BACKEND_URL` internal
- [ ] Worker service running (`python -m app.worker`)
- [ ] DNS alias, `https://$DOMAIN/health` and `/api/health/ready` OK
