# HTTP API

Base path: `/api`. FastAPI OpenAPI: `http://localhost:8000/docs` when the backend is running.

The Next.js origin proxies `/api/*` to the backend. Passage SSR bypasses the rewrite and calls `NLP_BACKEND_URL` directly.

## Headers

| Header | Used by | Notes |
| ------ | ------- | ----- |
| `X-Device-Id` | `GET /library`, `GET /passages/{id}/stats`, `POST /feedback`, `POST /generate` (sent by the client; generate does not read it) | Must match `^[A-Za-z0-9_-]{8,64}$`. Invalid or missing → treated as anonymous (default placement A2, no lemma/read history). The browser stores a UUID in `localStorage` as `levla.device_id`. |
| `Content-Type: application/json` | POST bodies | |

CORS: `CORS_ORIGINS` (default localhost:3000). Methods and headers are open (`*`).

## Endpoints

| Method | Path | Body / query | Success |
| ------ | ---- | ------------ | ------- |
| `GET` | `/health` | | `{ "ok": true, "name": "levla" }` |
| `POST` | `/generate` | `{ level, topic, genre?, language }` | `PassageResponse` |
| `GET` | `/library?language=ja\|ru` | `X-Device-Id` | `LibraryResponse` |
| `GET` | `/passages/{id}` | | `PassageResponse` |
| `GET` | `/passages/{id}/translation` | | `{ passage_id, translation }` |
| `GET` | `/passages/{id}/stats` | `X-Device-Id` | `PassageStats` |
| `POST` | `/gloss` | `{ word, passage_id? }` | `GlossResponse` |
| `POST` | `/feedback` | `{ passage_id, rating }` + `X-Device-Id` | `FeedbackResponse` |

`GET /library` defaults `language` to `ja` if omitted. `POST /generate` defaults `language` to `ru` if omitted (the UI always sends a language; the shelf defaults to Japanese).

### Status codes

| Code | When |
| ---- | ---- |
| 400 | `language` is not `ru` or `ja` on `/library` |
| 404 | Unknown passage id (passage, translation, stats, feedback) |
| 422 | Pydantic validation (level, topic length, rating enum, …) |
| 502 | Generation threw after the key was present |
| 503 | `OPENROUTER_API_KEY` missing on generate; translation still unavailable |

Error body is FastAPI’s usual `{ "detail": "…" }` (string or validation-error list). The frontend concatenates `detail[].msg` when `detail` is an array.

## Generate

```json
{
  "level": "A2",
  "topic": "a quiet morning at the market",
  "genre": "daily_life",
  "language": "ja"
}
```

| Field | Type | Rules |
| ----- | ---- | ----- |
| `level` | `"A1" \| "A2" \| "B1" \| "B2"` | required |
| `topic` | string | 1–200 chars |
| `genre` | string or null | optional; UI uses `daily_life`, `travel`, `news`, `folklore`, `work` (max 40). Unknown values are stored but do not add a prompt hint |
| `language` | `"ru" \| "ja"` | default `ru` |

This call is slow (LLM + morph + optional rewrite + translation). Timeouts on the OpenRouter client are 45s per completion.

## Passage (`PassageResponse`)

```json
{
  "id": "uuid",
  "language": "ja",
  "level": "A2",
  "topic": "a quiet morning at the market",
  "genre": "daily_life",
  "title": "市場の朝",
  "text": "…full source text…",
  "tokens": [ "…" ],
  "calibration": { "…" },
  "word_count": 86,
  "created_at": "2026-08-31T00:00:00Z",
  "translation": "In the morning…"
}
```

`word_count` is the number of `is_word` tokens, not whitespace-separated words.

### Token

What the reader clicks.

```json
{
  "text": "市場",
  "ws": "に",
  "is_word": true,
  "lemma": "市場",
  "morph": {
    "lemma": "市場",
    "pos": "noun",
    "case": null,
    "gender": null,
    "number": null,
    "tense": null,
    "aspect": null,
    "mood": null,
    "reading": "しじょう",
    "form": null
  },
  "gloss": "market",
  "level": "A2",
  "kanji": [
    {
      "char": "市",
      "reading": "し",
      "on": ["し"],
      "kun": ["いち"],
      "meaning": "market, city, town"
    },
    {
      "char": "場",
      "reading": "じょう",
      "on": ["じょう"],
      "kun": ["ば"],
      "meaning": "location, place"
    }
  ]
}
```

Whitespace (or the next Japanese morpheme, including particles that Sudachi split off) is on `ws` so the original orthography round-trips. Russian `ws` is typically a space or punctuation gap from razdel.

`is_word` is false for punctuation and Japanese 補助記号 / 空白.

Russian `morph.pos` uses pymorphy tags (`NOUN`, `VERB`, `ADJF`, …). Japanese POS is mapped to English labels (`noun`, `verb`, `i-adj`, `particle`, `aux`, …). Japanese `form` is Sudachi inflection (e.g. `連体形`, `仮定形`).

`level` is the lexicon band for the lemma, or `null` if unknown.

### Calibration

Present on every stored passage.

```json
{
  "passed": false,
  "attempts": 2,
  "overlevel_lemma_rate": 0.21,
  "subordinate_rate": 0.0,
  "forbidden_case_rate": 0.0,
  "forbidden_tense_rate": 0.0,
  "forbidden_pos_rate": 0.0,
  "flags": ["ja:te_iru (て)", "lemma:頑張る=unknown"],
  "warnings": [
    "Passage still has out-of-level structures. Read the flags; this is a soft-fail."
  ]
}
```

Soft-fail passages are still readable. The reader concatenates `warnings` under the article. Japanese unused rate fields (`forbidden_case_rate`, `forbidden_tense_rate`) are stored as `0`. `attempts` is 1 or 2.

## Library

```json
{
  "language": "ja",
  "placement": "A2",
  "next_id": "…",
  "seen_lemmas": 42,
  "items": [
    {
      "id": "…",
      "language": "ja",
      "level": "A2",
      "topic": "…",
      "genre": "daily_life",
      "title": "…",
      "word_count": 86,
      "created_at": "…",
      "passed": true,
      "read": false,
      "recommended": true,
      "new_lemmas": 12,
      "recycled_lemmas": 40
    }
  ]
}
```

`new_lemmas` / `recycled_lemmas` are **token occurrence counts** of content words, not unique lemmas. Sort on the backend: recommended first, then unread, then level, then newest.

`seen_lemmas` is unique lemmas stored for this device + language.

## Passage stats

Subset used by the reader header and “read next” before feedback:

`{ passage_id, language, placement, read, new_lemmas, recycled_lemmas, next_id }`

`next_id` excludes the current passage.

## Translation

`GET /passages/{id}/translation` returns the stored English string, or generates, stores, and returns it. 503 if the LLM is missing or fails and nothing was stored. Seeded passages have translations in `seed_translations.py`.

## Gloss

```json
{ "word": "市場", "passage_id": "optional-uuid" }
```

If `passage_id` is set, the first token on that passage whose `text` equals `word` is returned (including stored gloss, CEFR band, kanji). Otherwise the word is analyzed live and looked up in the lexicon only (no CEFR band, no LLM fill on this path).

The reader does **not** call `/gloss` today; it uses tokens already on the passage. The endpoint is for live lookup and future use.

## Feedback

```json
{ "passage_id": "…", "rating": "too_easy" }
```

`rating` is `too_easy` | `too_hard`.

```json
{
  "ok": true,
  "passage_id": "…",
  "rating": "too_easy",
  "placement": "B1",
  "next_id": "…",
  "new_lemmas": 12,
  "recycled_lemmas": 40
}
```

Without a valid `X-Device-Id`, `placement` and `next_id` are null and lemma counts stay 0, but the anonymous `feedback` row is still written.
