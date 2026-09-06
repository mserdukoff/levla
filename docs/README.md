# Levla documentation

This folder is the product, technical, and design specification for Levla. It describes the running app, not the original six-week plan in `plan.md`.

| Document | What it covers |
| -------- | -------------- |
| [Product](./product.md) | Why Levla exists, who it is for, the reading loop, scope |
| [Architecture](./architecture.md) | Stack, repo layout, request flow, persistence, deploy |
| [Design](./design.md) | Visual language, typography, layouts, components, interaction |
| [API](./api.md) | HTTP endpoints, headers, payloads, error codes |
| [NLP and CEFR](./nlp-and-cefr.md) | Generation, analyzers, validators, lexicons, kanji |
| [Learner model](./learner-model.md) | Device identity, placement, lemmas, next-text ranking |
| [AWS](./aws.md) | Step-by-step hosting on ECS Fargate, ALB, RDS, and S3 |

For a shorter operator’s guide (how to run, env vars, tests), see the [root README](../README.md).
