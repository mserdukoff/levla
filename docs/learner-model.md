# Learner model

No accounts. The browser stores a UUID in `localStorage` (`levla.device_id`) and sends it as `X-Device-Id`. Language preference is stored separately (`levla.language`, default Japanese).

A valid device id matches `^[A-Za-z0-9_-]{8,64}$`. Anything else is ignored: the shelf still loads, but placement stays A2 and no lemmas or reads are recorded.

Per `(device_id, language)` Levla keeps:

| Table | Role |
| ----- | ---- |
| `learners` | Current CEFR placement (default **A2**). Unique on `(device_id, language)` |
| `learner_lemmas` | Content-word lemmas seen after finishing a text. Unique on `(device_id, language, lemma)` |
| `learner_stars` | Lemmas the learner saved from a gloss. Unique on `(device_id, language, lemma)` |
| `learner_reads` | Passages already read. Unique on `(device_id, passage_id)` — language is implied by the passage |
| `feedback` | Raw too-easy / just-right / too-hard events (not device-scoped) |

Reads and lemmas are written only in `complete_read` (the **Too easy / Just right / Too hard** path). Opening a passage does not mark it read and does not ingest lemmas. Starring a word does not ingest it into `learner_lemmas`.

## Placement

`too_easy` moves one step up (cap **B2**). `too_hard` moves one step down (floor **A1**). `just_right` keeps the current band. All three ingest lemmas, mark the passage read, and pick next.

```
A1 ⇄ A2 ⇄ B1 ⇄ B2
```

There is no half-step, no consecutive-rating hysteresis, and no use of calibration `passed` when bumping. A soft-fail A2 text marked too hard still moves the learner to A1.

Japanese and Russian placements are independent rows.

## New vs. known

Content POS only:

- **Russian:** `NOUN`, `ADJF`, `ADJS`, `VERB`, `INFN`, `ADVB`, `PRED`, `NUMR`
- **Japanese:** `noun`, `verb`, `i-adj`, `na-adj`, `adverb`

Counts on the shelf and reader are **token occurrences**, not unique lemmas. A recycled word that appears three times counts as three “known.” Unique lemmas are what get stored in `learner_lemmas` and what `seen_lemmas` reports on the shelf line.

Ingest happens **before** the level bump, using the seen-set from before this passage, so the `new_lemmas` / `recycled_lemmas` on the feedback response describe the text just finished.

## Next text

`pick_next_id` walks unread, non-excluded passages in this level order:

1. current placement
2. one level up (if any)
3. one level down (if any)
4. the rest of A1–B2

Within a band, **calibration-passed** texts win over soft-fails, then **newer** `created_at` wins. If every passage is already read, it still returns something (the best-scoring row, including already-read).

The recommended item is `next_id` and is highlighted as **Continue**. The reader’s stats `next_id` excludes the current passage so “Read next” is not a self-link.

## What the model is not

- Not spaced repetition. Lemmas are a set, not a schedule or strength. Saved Words are a list, not a review queue.
- Not click-based for placement. Tapping a gloss does not add a lemma to `learner_lemmas`; finishing via feedback does. **Save** only writes `learner_stars`.
- Not cross-device. Clearing site data is a full reset of client identity.
- Not a proficiency exam. Placement is a one-step slider driven by self-report.

The shelf copy “Rate a passage to move it” is the entire onboarding for this model.
