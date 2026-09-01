# Product

## Objective

Levla is a **CEFR-calibrated graded reader** for **Russian** and **Japanese** (A1–B2).

It generates and serves short reading passages at a checkable CEFR band, then lets the learner tap any word for lemma, grammar, gloss, and (in Japanese) kanji. After each text the learner marks it **too easy**, **just right**, or **too hard**. That updates placement (or leaves it), records the lemmas they just saw, and picks the next unread passage.

The product claim is not “an LLM wrote some Japanese.” It is:

> Grammar and vocabulary are constrained in the prompt, then checked by a morphological analyzer, then used to drive a learner model.

Asking a model to “write B1 Russian” or “write A1 Japanese” is not enough. Russian drifts into extra cases and participles. Japanese drifts into て-form, ている, relative clauses, and keigo. Levla treats CEFR as a **checkable constraint**, not a prompt adjective.

## Who it is for

Serious hobbyists and heritage learners of Russian or Japanese who have hit the graded-reader gap: native material is too hard, textbook dialogues are too short and too fake, and LLM “write me A2 Japanese” output is not actually A2.

The app is a **single-user demo**, not a multi-tenant product. There are no accounts, billing, or sync across devices.

## What the learner can do

Two screens. That is the whole product.

### Shelf (`/`)

- Switch between Japanese and Russian.
- See current placement for that language (default **A2**) and how many lemmas have been seen.
- Open a **Continue** recommendation, or any other title on the shelf.
- Each card shows CEFR band, topic, word count, **new vs. known** content-word tokens, and whether the passage has already been read.
- **Restock the shelf**: generate a new passage for the current language, a CEFR level, a topic, and an optional genre (daily life, travel, news, folklore, work).

### Reader (`/passage/[id]`)

- Read the passage as clickable words. Tap a word for:
  - surface form, lemma, CEFR band
  - Russian: case, gender, number, tense, aspect, mood
  - Japanese: reading (hiragana), particle/verb role, verb-suffix breakdown (stem + polite/past/te-form/…), kanji breakdown with on/kun, meanings, strokes, JLPT, grade, frequency, radical, and parts
  - English gloss
- Optionally **colour grammar**: particles (は topic, が subject, を object, others), verbs, endings, adjectives. Off by default; persists in `localStorage`.
- Optionally **furigana** over kanji (Japanese). Off by default.
- Optionally **fade known** content words the learner has already finished in other texts.
- Save a lemma from the gloss; a **Words** list on the shelf (not SRS).
- Reveal a full **English** translation, or **this sentence** only.
- Mark the text **too easy**, **just right**, or **too hard**. Too easy / too hard move placement one CEFR step. Just right keeps the level. All three ingest lemmas and pick **Read next**.

### Seeded library

On first backend start, Levla writes a hand-authored starter library (and English translations) if they are missing or failed calibration:

| Language | A1 | A2 | B1 | B2 |
| -------- | -- | -- | -- | -- |
| Japanese | 4  | 4  | 3  | 2  |
| Russian  | 4  | 4  | 3  | 2  |

Generated texts are stored alongside these and appear on the same shelf.

## Core loop

```
open shelf  →  pick Continue (or any card)
     →  read, tap words for gloss
     →  Too easy / Just right / Too hard
     →  placement ±1 (or unchanged), lemmas stored, Read next
     →  back on the shelf at a new recommendation
```

Optional side path: **Restock the shelf** → wait 20–40 seconds for constrained generation + validation → land on the new reader.

## Positioning vs. plan.md

`plan.md` is the original Russian-only v1 sketch (Grammario lineage, paywall stub, r/Russian beta). The running app diverged:

| Plan v1 | Built |
| ------- | ----- |
| Russian only | Russian **and** Japanese |
| Lightweight auth + paywall stub | No accounts; `localStorage` device UUID |
| 300–800 word Russian passages | Russian 400–700 words; Japanese 22–40 short sentences |
| Hard reject on failed calibration | Soft fail: store the closer draft, show a warning |
| Monetization ($5–8/mo) | Not implemented |

Not in this repo: audio, SRS / Anki export, billed accounts, official CEFR or JLPT word lists, C1/C2, or languages other than `ru` and `ja`.

## Success criteria (from the original plan, still relevant)

Do not add languages, audio, or SRS until there is signal this loop works:

- Testers return for a second or third passage without prompting.
- “Too hard” rate is low enough that CEFR labeling is credible.
- Unsolicited comments name the retained hook (comprehension confidence, click-gloss, topic novelty).
