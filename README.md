# Levla

CEFR-calibrated graded readers for **Russian** and **Japanese**.

Levla generates and serves short reading passages at a real A1–B2 level, then lets you tap any word for lemma, grammar, gloss, and (in Japanese) kanji. After each text you mark it **too easy**, **just right**, or **too hard**. That updates your placement (or leaves it), records the lemmas you just saw, and picks the next unread passage.

The product claim is not “an LLM wrote some Japanese.” It is: **grammar and vocabulary are constrained in the prompt, then checked by a morphological analyzer, then used to drive a learner model.**

---

Full product, architecture, design, API, NLP, and learner-model specs live in [`docs/`](docs/README.md).

## Contents

- [Why it exists](#why-it-exists)
- [What you can do](#what-you-can-do)
- [How a passage is made](#how-a-passage-is-made)
- [CEFR rules](#cefr-rules)
- [Learner model](#learner-model)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Data](#data)
- [API](#api)
- [Frontend](#frontend)
- [Run locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Tests](#tests)
- [Rebuilding lexicons](#rebuilding-lexicons)
- [Environment](#environment)
- [Limitations](#limitations)
- [Documentation](#documentation)

---

## Why it exists

Asking a model to “write B1 Russian” or “write A1 Japanese” is not enough. Russian drifts into extra cases and participles. Japanese drifts into て-form, ている, relative clauses, and keigo. Levla treats CEFR as a **checkable constraint**:

1. The prompt includes per-level grammar rules and an in-band lemma sample.
2. The draft is tokenized with a real analyzer (pymorphy3 for Russian, Sudachi for Japanese).
3. A validator scores over-level lemmas and forbidden constructions.
4. A failing draft is rewritten with those flags. The closer attempt is kept.
5. The reader still shows a warning if the text is a soft fail.

The reading UI is built around that analysis: every word already has lemma, POS, gloss, CEFR band, grammar role, verb-suffix pieces, and kanji parts attached before it hits the page.

---

## What you can do

**Landing (`/`)**

- A landing page that states the claim (CEFR as a checked constraint), runs the real reader on a sample passage, and links into the library.

**Shelf (`/library`)**

- Switch between Japanese and Russian.
- See your current placement for that language and how many lemmas you have seen.
- Open a **Continue** recommendation, or any other title on the shelf.
- Each card shows CEFR band, topic, word count, **new vs. known** content words, and whether you have already read it.
- **Restock the shelf**: generate a new passage for the current language, a CEFR level, a topic, and an optional genre (daily life, travel, news, folklore, work).

**Reader (`/passage/[id]`)**

- Read the passage as clickable words. Tap a word for:
  - surface form, lemma, CEFR band
  - Russian: case, gender, number, tense, aspect, mood
  - Japanese: reading (hiragana), particle/verb role, verb-suffix breakdown, kanji breakdown with on/kun, meanings, strokes, JLPT, grade, frequency, radical, parts, and a stroke-order diagram that plays as soon as the gloss opens.
  - English gloss
- Optionally colour grammar (particles, verbs, endings, adjectives). Off by default.
- Optionally furigana over kanji (Japanese), and fade already-seen content words.
- Save a lemma from the gloss; it appears on a **Words** list on the shelf, with stroke-order diagrams for Japanese.
- Reveal a full **English** translation, or **this sentence** only.
- Mark the text **too easy**, **just right**, or **too hard**. Too easy / too hard move placement one CEFR step. Just right keeps it. All three ingest lemmas and give you **Read next**.

**Seeded library**

On first backend start, Levla writes a hand-authored starter library (and English translations) if they are missing or failed calibration:

| Language | A1 | A2 | B1 | B2 |
| -------- | -- | -- | -- | -- |
| Japanese | 4  | 4  | 3  | 2  |
| Russian  | 4  | 4  | 3  | 2  |

Generated texts are stored alongside these and appear on the same shelf.

---

## How a passage is made

```
topic + CEFR + genre + language
        │
        ▼
  LLM (OpenRouter)  ── grammar constraints + lemma sample
        │
        ▼
  Morphological analysis  ── tokens, lemmas, POS, readings
        │
        ▼
  Gloss attach  ── lexicon first, LLM fallback for missing lemmas
        │
        ▼
  CEFR validator  ── rates + flags
        │
        ├── pass → persist
        └── fail → rewrite with flags → keep the less-severe draft
        │
        ▼
  English translation (best-effort)
        │
        ▼
  SQLite  →  reader
```

**Generation** (`backend/app/services/llm.py`, `generate.py`)

- Model defaults to `openai/gpt-4o-mini` via OpenRouter. Override with `LLM_MODEL`.
- Prompt includes:
  - language-specific length (Russian: 400–700 words; Japanese: 22–40 short sentences)
  - `prompt_constraints` from `data/grammar/{ru,ja}_cefr.json`
  - a random sample of ~48 lemmas at or below the target band
  - genre hint, if any
- Response must be JSON `{ "title", "text" }`.
- If calibration fails, a second call is made at lower temperature with the validator flags. Severity is `flags + weighted rates`. The less-severe attempt is stored even if it still fails (soft fail + warning).

**Analysis**

- Russian: [razdel](https://github.com/natasha/razdel) tokenizes; [pymorphy3](https://github.com/no-plagiarism/pymorphy3) lemmatizes and tags case / gender / number / tense / aspect / mood.
- Japanese: [Sudachi](https://github.com/WorksApplications/Sudachi) in split mode C. POS is mapped to English labels (`noun`, `verb`, `i-adj`, `particle`, …). Readings are converted to hiragana. Kanji in the surface form are aligned to slices of that reading.

**Glosses**

Lexicon lookup (`data/gloss/{ru,ja}_en.json`). Unknown lemmas in generated text get a one-shot LLM batch gloss. Click-to-gloss on a live passage prefers the token already stored on that passage.

**Kanji** (`backend/app/services/kanji.py`)

For each kanji in a word, Levla tries to consume a prefix of the word reading using on/kun candidates (including voiced, handakuten, and sokuon variants). Each part carries the matched reading, on (katakana) / kun (okurigana dots), English meanings, stroke count, JLPT N-level, school grade, newspaper frequency, Kangxi radical, and KRADFILE parts from `data/kanji/ja.json` (~13k characters, built from KANJIDIC2). Stored passages are re-aligned on read so the extra fields show up without regenerating text.

Jisho.org has no kanji API (its public endpoint is word search only). The lexicon is the same EDRDG data Jisho is built on, bundled locally. Stroke-order diagrams in the gloss use [KanjiVG](https://kanjivg.tagaini.net/) (the same source Jisho animates): opening a word fetches its SVG, then Levla draws the strokes in Japanese order.

---

## CEFR rules

Rules live in JSON, not in prompt folklore. Validators in `backend/app/services/validator.py` and `validator_ja.py` compute rates and emit flags the LLM can be asked to fix.

### Russian (`data/grammar/ru_cefr.json`)

Checked against pymorphy tags: allowed cases and tenses, forbidden POS (participles, verbal adverbs, comparatives), forbidden conjunctions, subordinate-clause rate, over-level lemma rate. Sentence-initial *когда* is treated as “when (time)”, not a subordinate conjunction.

| Level | Grammar (simplified) |
| ----- | -------------------- |
| **A1** | Nominative + present only. No subordinates. No participles / gerunds / comparatives. |
| **A2** | Nom, acc, gen, prep, dat. Present / past / future. *когда / если / потому* allowed sparingly. No instrumental, no *который*, no *бы*. |
| **B1** | All six cases. Aspect contrast, motion verbs, reflexives, imperatives. Simple subordinates. Still no participles / gerunds / *бы*. |
| **B2** | Full case system. Participles, verbal adverbs, *бы*, *который*-clauses allowed. Vocab still capped at B2. |

A1 Russian also skips likely proper names when scoring unknown lemmas (capitalized non-initial nouns).

### Japanese (`data/grammar/ja_cefr.json`)

Constructions are detected from Sudachi tokens (particles, auxiliaries, inflection form), not from the LLM’s opinion:

| Flag | Roughly |
| ---- | ------- |
| `te_form` | て / で as a particle |
| `te_iru` | て + いる / おる |
| `plain_past` | た / だ without ます / です |
| `plain_neg` | ない without ます / です |
| `conditional` | ば / たら / なら / 仮定形 |
| `potential` / `passive` | れる / られる |
| `causative` | させる / せる |
| `relative` | 連体形 verb modifying a noun |
| `keigo` | いらっしゃる, おっしゃる, いただく, ございます, … |

| Level | Allowed (simplified) |
| ----- | -------------------- |
| **A1** | です/ます only. Core particles. No て-form, plain past/neg, ている, conditionals, potential, causative, passive, relatives, keigo. |
| **A2** | て-form, てください, plain た / ない. Still no ている, conditionals, potential, causative, passive, relatives, keigo. |
| **B1** | ている, potential, causative, simple relatives, ば/たら/なら. No passive-as-voice, no keigo. |
| **B2** | Passive and modest keigo allowed. Vocab aimed at B2 / N3–N2. |

A draft **passes** only if over-level lemma rate, construction hits, and (for Russian) case/tense/POS/subordinate rates all sit under the caps in the JSON. Lemma flags are truncated to 12 so the correction prompt stays readable.

---

## Learner model

No accounts. The browser stores a UUID in `localStorage` (`levla.device_id`) and sends it as `X-Device-Id`. Language preference is stored separately (`levla.language`).

Per `(device_id, language)` Levla keeps:

| Table | Role |
| ----- | ---- |
| `learners` | Current CEFR placement (default **A2**) |
| `learner_lemmas` | Content-word lemmas seen after finishing a text |
| `learner_stars` | Lemmas saved from the gloss |
| `learner_reads` | Passages already read |
| `feedback` | Raw too-easy / just-right / too-hard events |

**Placement.** `too_easy` moves one step up (cap B2). `too_hard` moves one step down (floor A1). `just_right` keeps the current band.

**New vs. known.** Content POS only:

- Russian: noun, adjective, verb, adverb, predicative, numeral
- Japanese: noun, verb, i-adj, na-adj, adverb

Counts are **token occurrences**, not unique lemmas. The shelf uses this so a recycled word that appears three times counts as three “known.”

**Next text.** Prefer unread, calibration-passed passages at the current level, then one level up, then one down, then the rest of the scale. Within a band, newer texts win. The recommended item is highlighted as **Continue**.

---

## Architecture

```
┌─────────────────────────────┐     /api proxy          ┌─────────────────────────────┐
│  Next.js 16 (React 19)      │ ──────────────────────► │  FastAPI                    │
│  frontend/                  │                         │  backend/                   │
│  :3000                      │  SSR fetch for reader   │  :8000                      │
│                             │ ──────────────────────► │                             │
│  Shelf, Reader, Generate    │                         │  generate / validate / NLP  │
└─────────────────────────────┘                         └──────────────┬──────────────┘
                                                                       │
                                                                       ▼
                                                            Postgres (Compose / AWS)
                                                            or SQLite (local)
                                                            data/*.json lexicons
                                                            S3 audio (optional)
                                                            OpenRouter (optional)
```

- **Frontend** talks to `/api/...` on its own origin. Next.js proxies those paths to `NLP_BACKEND_URL` (default `http://127.0.0.1:8000`) at runtime.
- Passage pages are **dynamic** (`force-dynamic`, `cache: "no-store"`). The server fetches `/api/passages/:id` at request time so the first paint already has tokens.
- **Backend** is a sync FastAPI app (SQLAlchemy session per request). On startup it waits for the database, creates tables, and seeds the library.

---

## Repository layout

```
levla/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, lifespan → init_db
│   │   ├── api/routes.py           # HTTP API
│   │   ├── core/config.py          # env (OpenRouter, DB, CORS, data dir)
│   │   ├── models/
│   │   │   ├── db.py               # SQLAlchemy tables
│   │   │   └── schemas.py          # Pydantic request/response models
│   │   └── services/
│   │       ├── generate.py         # generate, persist, feedback, translation
│   │       ├── llm.py              # OpenRouter: passage, gloss, translate
│   │       ├── morph.py            # language dispatcher
│   │       ├── morph_ja.py         # Sudachi
│   │       ├── validator.py        # Russian CEFR + ja dispatch
│   │       ├── validator_ja.py     # Japanese constructions
│   │       ├── gloss.py            # lexicon + LLM fill
│   │       ├── kanji.py            # reading alignment + KANJIDIC2 details
│   │       ├── grammar.py          # colour roles + Japanese verb suffixes
│   │       ├── learner.py          # placement, lemmas, next-id
│   │       ├── library.py          # shelf payload
│   │       ├── data.py             # load grammar / vocab / gloss JSON
│   │       ├── seed.py             # hand-authored library
│   │       └── seed_translations.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/app/                    # `/` landing, `/library` shelf, `/passage/[id]` reader
│   ├── src/components/             # Shelf, Reader, GenerateForm, GlossCard
│   ├── src/lib/                    # API client, types, device id, KanjiVG parser
│   ├── next.config.ts
│   └── Dockerfile
├── data/
│   ├── grammar/{ru,ja}_cefr.json
│   ├── vocab/{ru,ja}_cefr.json
│   ├── gloss/{ru,ja}_en.json
│   └── kanji/ja.json
├── scripts/
│   ├── build_lexicon.py            # Russian vocab + gloss
│   ├── build_ja_lexicon.py         # Japanese vocab + gloss
│   └── build_kanji.py              # KANJIDIC2 + KRADFILE + JLPT → ja.json
└── docker-compose.yml
```

---

## Data

| File | Size (approx.) | Purpose |
| ---- | -------------- | ------- |
| `data/vocab/ru_cefr.json` | ~5,400 lemmas | Lemma → A1–B2. Pedagogical core plus frequency banding from a 50k word list. |
| `data/vocab/ja_cefr.json` | ~500 lemmas | Pedagogical Japanese core, dictionary form. |
| `data/gloss/ru_en.json` | ~1,360 | Short English glosses (pedagogical overlay; not every frequency lemma has a gloss). |
| `data/gloss/ja_en.json` | ~500 | Short English glosses, keyed to Sudachi dictionary form. |
| `data/grammar/ru_cefr.json` | 4 levels | Allowed cases/tenses, forbidden POS/conjunctions, rate caps, prompt text. |
| `data/grammar/ja_cefr.json` | 4 levels | Forbidden constructions/lemmas, rate caps, prompt text. |
| `data/kanji/ja.json` | ~13,100 | Character → on, kun, meanings, strokes, JLPT, grade, freq, radical, parts. |

Russian vocab bands are TORFL-inspired pedagogical assignments plus frequency ranks (top ~500 → A1, ~1500 A2, ~3000 B1, rest of the kept list B2). They are **not** a licensed official word list. Japanese vocab is a curated N5–N3-ish core, not JLPT official lists. Kanji JLPT tags on the gloss card come from [kanjiapi.dev](https://kanjiapi.dev/) (Jonathan Waller’s lists); readings, meanings, strokes, grade, frequency, and radicals come from [KANJIDIC2](https://www.edrdg.org/wiki/KANJIDIC_Project.html) and [KRADFILE](https://www.edrdg.org/krad/kradinf.html), used under the [EDRDG licence](https://www.edrdg.org/edrdg/licence.html). Stroke-order diagrams are [KanjiVG](https://kanjivg.tagaini.net/), © Ulrich Apel, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

`data/raw/` is gitignored. `scripts/build_lexicon.py` expects `data/raw/ru_50k.txt` if you rebuild Russian from frequency. `scripts/build_kanji.py` downloads KANJIDIC2, KRADFILE, and JLPT lists into `data/raw/` then writes `data/kanji/ja.json`.

---

## API

Base path: `/api`. OpenAPI is at `http://localhost:8000/docs` when the backend is running.

| Method | Path | Body / query | Notes |
| ------ | ---- | ------------ | ----- |
| `GET` | `/health` | | `{ "ok": true, "name": "levla" }` |
| `POST` | `/generate` | `{ level, topic, genre?, language }` | **200** cached passage, or **202** job id to poll |
| `GET` | `/generate/{job_id}` | header `X-Device-Id` | Job status; includes `passage` when complete |
| `GET` | `/library?language=ja\|ru` | header `X-Device-Id` | Placement, seen lemma count, `next_id`, items with new/known/read/recommended. |
| `GET` | `/passages/{id}` | | Full passage: text, tokens, calibration, optional translation. |
| `GET` | `/passages/{id}/translation` | | Returns stored English or generates and stores it. 503 if still unavailable. |
| `GET` | `/passages/{id}/stats` | header `X-Device-Id` | Placement, read flag, new/recycled counts, `next_id`, `known_lemmas`, `starred_lemmas`. |
| `POST` | `/gloss` | `{ word, passage_id? }` | Prefers the passage token; else live analyze + lexicon. |
| `POST` | `/feedback` | `{ passage_id, rating }` + `X-Device-Id` | `too_easy` \| `just_right` \| `too_hard`. Ingests lemmas, bumps level (except just_right), returns next id. |
| `GET` | `/words?language=ja\|ru` | header `X-Device-Id` | Starred lemmas for the Words list. |
| `POST` | `/words` | `{ lemma, gloss?, passage_id?, language? }` + `X-Device-Id` | Save a lemma from the gloss. |
| `DELETE` | `/words` | `{ lemma, language }` + `X-Device-Id` | Remove a starred lemma. |

**Generate request**

```json
{
  "level": "A2",
  "topic": "a quiet morning at the market",
  "genre": "daily_life",
  "language": "ja"
}
```

`level` is `A1` | `A2` | `B1` | `B2`. `language` is `ru` | `ja` (default `ru` on the API; the UI defaults to Japanese). `genre` is optional: `daily_life`, `travel`, `news`, `folklore`, `work`.

**Token** (what the reader clicks)

```json
{
  "text": "市場",
  "ws": "に",
  "is_word": true,
  "lemma": "市場",
  "morph": { "lemma": "市場", "pos": "noun", "reading": "しじょう", "form": null },
  "gloss": "market",
  "level": "A2",
  "kanji": [
    { "char": "市", "reading": "し", "on": ["シ"], "kun": ["いち"], "meaning": "market, city, town", "strokes": 5, "jlpt": 3, "grade": 2, "freq": 42, "radical": "巾", "radical_name": "turban", "parts": ["巾", "亠"], "nanori": ["い", "ち"] },
    { "char": "場", "reading": "じょう", "on": ["ジョウ", "チョウ"], "kun": ["ば"], "meaning": "location, place", "strokes": 12, "jlpt": 4, "grade": 2, "freq": 52, "radical": "土", "radical_name": "earth", "parts": ["土", "日", "勿"], "nanori": [] }
  ]
}
```

Whitespace between Japanese morphemes is preserved on `ws` so the original orthography (no extra spaces) round-trips.

**Calibration** on every stored passage: `passed`, `attempts` (1 or 2), rates, `flags`, `warnings`. Soft-fail passages are still readable; the reader shows the warning string.

---

## Frontend

| File | Role |
| ---- | ---- |
| `src/app/page.tsx` | Home: title + `Shelf` |
| `src/components/shelf.tsx` | Language toggle, continue card, rest of library, restock form |
| `src/components/generate-form.tsx` | Level / topic / genre → `POST /api/generate` |
| `src/app/passage/[id]/page.tsx` | Server-fetches passage, renders `Reader` |
| `src/components/reader.tsx` | Clickable tokens, gloss card, English toggle, feedback bar |
| `src/lib/api.ts` | Fetch helpers; JSON `detail` errors from FastAPI |
| `src/lib/device.ts` | Device UUID + language in `localStorage` |
| `src/lib/types.ts` | Shared TS types, CEFR/genre/language labels, morph formatting |

UI is a paper/ink/terracotta palette (`src/app/globals.css`). Display and Russian reading use Literata (Cyrillic subset). Japanese uses Outfit plus system Gothic (`Hiragino`, `Yu Gothic`, `Noto Sans JP`).

Generation is slow on purpose (20–40 seconds is the expected wait): write, analyze, maybe rewrite, translate.

---

## Run locally

Needs **Python 3.12+**, **Node 20+**, and an [OpenRouter](https://openrouter.ai/) key if you want generation and live translations. The seed library and tap-to-gloss work without a key.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# set OPENROUTER_API_KEY=sk-or-...

uvicorn app.main:app --reload --port 8000
```

SQLite file defaults to `backend/levla.db`. First boot creates tables and seeds the library (this can take a few seconds while every seed text is analyzed).

### Frontend

```bash
cd frontend
npm install
# optional: NLP_BACKEND_URL=http://127.0.0.1:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

If the rewrite target is wrong you will see shelf errors; the Next server must be able to reach the FastAPI process.

---

## Run with Docker

```bash
# backend/.env must exist (same keys as .env.example)
docker compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000)
- Database: Compose Postgres (`levla-pg`). Audio MP3s: named volume `levla-audio`
- The frontend container uses `NLP_BACKEND_URL=http://backend:8000` at **runtime** so `/api` and SSR stay on the Compose network
- Backend waits for Postgres, then creates tables and seeds the library on first boot

Images are production-shaped (non-root users, health checks, `APP_ENV=production` baked into the backend image). Compose overrides `APP_ENV=development` so a local `JWT_SECRET=dev-change-me` still boots. See [docs/aws.md](docs/aws.md) for ECS / RDS / S3.

---

## Tests

From `backend/` with the venv active and `PYTHONPATH` already set by `pytest.ini`:

```bash
cd backend
pytest
```

| File | Covers |
| ---- | ------ |
| `tests/test_validator.py` | Russian lemmas/cases; A1 rejects past, accusative, *если*; A2 allows acc, rejects instrumental |
| `tests/test_validator_ja.py` | です/ます A1; て-form A1 vs A2; ている A2 vs B1; keigo B1 vs B2; core gloss |
| `tests/test_kanji.py` | Reading alignment: 市場, 学生, 食べる, 本; dictionary fields on 本 / 語 |
| `tests/test_grammar.py` | は/が/を roles; 食べました / 食べる / て-いる / 行かない chains; Russian verb vs preposition |
| `tests/test_learner.py` | Placement bump, just-right no bump, new/known counts, next-id skip of already-read, star/unstar |
| `tests/test_sentences.py` | Japanese sentence index on 。; English split on `. ` |
| `tests/test_translation.py` | Every seed title has a non-empty English translation; persist path stores it |

Tests do **not** call OpenRouter. Gloss attach in tests uses `use_llm=False`.

---

## Rebuilding lexicons

Only needed if you change the pedagogical lists in the scripts.

```bash
# Japanese: writes data/vocab/ja_cefr.json and data/gloss/ja_en.json
python3 scripts/build_ja_lexicon.py

# Kanji: KANJIDIC2 + KRADFILE + JLPT lists → data/kanji/ja.json
python3 scripts/build_kanji.py

# Russian: needs pymorphy3 and optionally data/raw/ru_50k.txt
python3 scripts/build_lexicon.py
```

Grammar JSON is edited by hand. After changing grammar or vocab, restart the backend (loaders are `lru_cache`d). Re-seeded library rows that already passed calibration are left in place; failed ones are deleted and rewritten from `SEED`.

---

## Environment

**Backend** (`backend/.env`, see `backend/.env.example`)

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `OPENROUTER_API_KEY` | empty | Required for `/generate`, LLM gloss fill, and translation |
| `LLM_MODEL` | `openai/gpt-4o-mini` | OpenRouter model id |
| `DATABASE_URL` | `sqlite:///./levla.db` | SQLAlchemy URL. Compose sets Postgres. `postgres://` is rewritten to `postgresql+psycopg2://` |
| `DB_SSLMODE` | empty | Set `require` for RDS |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated. `PUBLIC_BASE_URL` is always added |
| `APP_ENV` | `development` | `production` requires a real `JWT_SECRET` and sets `Secure` cookies |
| `JWT_SECRET` | `dev-change-me` | Signs auth cookies |
| `PUBLIC_BASE_URL` | `http://localhost:3000` | Public origin (OAuth, CORS, OpenRouter referer) |
| `S3_AUDIO_BUCKET` | empty | If set, passage MP3s go to S3 instead of local disk |
| `SKIP_SEED` | `false` | Skip library/catalog seed (extra ECS tasks after first boot) |
| `GENERATE_WORKERS` | `2` | Background threads per process that run generation jobs. Set `0` on API tasks if a dedicated worker service handles generation |
| `GENERATE_MAX_PENDING` | `3` | Max queued/running jobs per device or signed-in user |

**Frontend**

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `NLP_BACKEND_URL` | `http://127.0.0.1:8000` | Backend origin for SSR passage fetch and the `/api` proxy. Read at runtime |

---

## Limitations

- **Soft fail.** A passage that still violates the ruleset is stored and readable, with a warning. Calibration is a gate with a retry, not a hard reject.
- **No accounts.** Clearing site data resets placement and seen lemmas. There is no sync across devices.
- **Lexicon coverage.** Japanese vocab is a few hundred lemmas; unknown content words count as over-level (names and some loanwords are skipped). Russian frequency lemmas without a pedagogical gloss may have no English until an LLM fill runs.
- **Analyzer errors.** pymorphy3 and Sudachi can pick the wrong lemma or POS; the validator will then flag or miss constructions.
- **Japanese construction detection** is heuristic (て+いる, 連体形+noun, a keigo lemma list). It will both over- and under-flag.
- **Generation cost and latency.** Two completion calls plus gloss plus translation is normal on a fail-then-rewrite path. No streaming.
- **SQLite.** Fine for a single-user or small demo. Compose and AWS use Postgres.
- **Languages.** Only `ru` and `ja`. Adding a language means grammar JSON, vocab/gloss, a morph module, a validator, seed texts, and UI labels.

Not in this repo: audio, SRS / Anki export, billed accounts, or official CEFR/JLPT lists.

---

## Documentation

| Doc | Covers |
| --- | ------ |
| [docs/product.md](docs/product.md) | Objective, audience, reading loop, scope vs. `plan.md` |
| [docs/architecture.md](docs/architecture.md) | Stack, request flow, SQLite, Docker, adding a language |
| [docs/design.md](docs/design.md) | Palette, type, layouts, components, interaction rules |
| [docs/api.md](docs/api.md) | Endpoints, headers, payloads, status codes |
| [docs/nlp-and-cefr.md](docs/nlp-and-cefr.md) | Generation, analyzers, validators, lexicons, kanji |
| [docs/learner-model.md](docs/learner-model.md) | Device id, placement, new/known counts, next-text ranking |
| [docs/aws.md](docs/aws.md) | Step-by-step AWS hosting (ECS, ALB, RDS, S3) |
