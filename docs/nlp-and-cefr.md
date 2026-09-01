# NLP and CEFR calibration

Levla’s differentiator is that CEFR is a **ruleset plus an analyzer**, not a prompt slogan.

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

## Generation (`llm.py`, `generate.py`)

- Model: `LLM_MODEL` (default `openai/gpt-4o-mini`) via OpenRouter (`https://openrouter.ai/api/v1`).
- First draft temperature **0.7**, 45s timeout. Correction pass **0.4**.
- Prompt includes:
  - language-specific length: Russian **400–700 words**; Japanese **22–40 short sentences**
  - `prompt_constraints` from `data/grammar/{ru,ja}_cefr.json` for that level
  - a deterministic-ish random sample of **~48 lemmas** at or below the target band (`random.Random(language + level + str(len(pool)))`)
  - genre hint, if the genre is one of `daily_life`, `travel`, `news`, `folklore`, `work`
  - script notes: Russian must mark ё and avoid Latin; Japanese must not insert spaces or furigana
- Response must be JSON `{ "title", "text" }`. Markdown fences and a greedy `{…}` extract are tolerated. Empty text raises. Empty title falls back to the topic.

If calibration fails, a second call is made with up to 20 validator flags. **Severity** is `flags + weighted rates` (see below). The less-severe attempt is stored even if it still fails.

Warnings that can land on the passage:

- Corrective rewrite was not closer to level; kept the first draft.
- Corrective rewrite failed; returning the first draft.
- Passage still has out-of-level structures. Read the flags; this is a soft-fail.
- Library text still has out-of-level flags. (seed path only)

Authored seed texts skip the LLM and skip LLM gloss fill (`use_llm_gloss=False`). They still run morph + lexicon + validator. Failed seed rows are deleted and rewritten on the next boot; passed rows are left in place (translation backfilled if missing).

### Genre hints (prompt only)

| id | Hint |
| -- | ---- |
| `daily_life` | everyday life, a small scene at home or in the city |
| `travel` | travel, a trip, a station or a new city |
| `news` | a short news-style report, still narrative, not a headline dump |
| `folklore` | a folk-tale or fable tone, simple characters |
| `work` | work, a workplace, colleagues, a task |

## Morphological analysis

Dispatcher: `morph.py` → `analyze_text` / `analyze_word`.

### Russian

- **razdel** splits the string; trailing whitespace between razdel tokens is stored on `ws`.
- A token is a word iff it contains Cyrillic (`[А-Яа-яЁё]`).
- **pymorphy3** supplies lemma (lowercased) and tags. Mapped to:

| pymorphy | Levla |
| -------- | ----- |
| case `nomn/gent/datv/accs/ablt/loct/voct` (+ gen2, acc2, loc2) | `nom / gen / dat / acc / ins / prep` (vocative → nom) |
| tense `pres/past/futr` | `pres / past / fut` |
| gender `masc/femn/neut` | `masc / fem / neut` |
| number `sing/plur` | `sg / pl` |
| aspect `impf/perf` | `impf / perf` |
| mood `indc/impr` | `indc / impr` |

POS is left as pymorphy (`NOUN`, `VERB`, `INFN`, `ADJF`, `PRTF`, `GRND`, …). CEFR band is `vocab_bands["ru"].get(lemma)`.

### Japanese

- **Sudachi** dictionary, **split mode C** (coarse; fewer morpheme cuts than A/B).
- POS 0 mapped through `POS_EN` (`名詞→noun`, `動詞→verb`, `形容詞→i-adj`, `形状詞→na-adj`, `助詞→particle`, `助動詞→aux`, …). Unknown POS 0 is kept as the Japanese label.
- `form` is POS slot 5 (inflection), e.g. `連体形`, `仮定形`.
- Reading: Sudachi `reading_form()` converted katakana→hiragana. Dropped when the surface is already kana-only and the reading equals the surface or lemma.
- Punctuation (`補助記号`) and whitespace (`空白`) are non-words.
- Kanji breakdown runs at tokenize time (and again on read if a stored token has an empty `kanji` list).

### Kanji (`kanji.py`)

`data/kanji/ja.json` (~13k characters): on, kun, meanings.

For each kanji in the surface, Levla tries to consume a **prefix of the remaining word reading** using on/kun candidates, including:

- dakuten (か→が)
- handakuten (は→ぱ)
- sokuon (く/き/ち/つ → っ)

Candidates are tried longest-first. Okurigana kana in the surface also advance the remaining reading. Each part carries the matched slice (or `null`), full on/kun lists, and up to three English meanings lowercased.

This is heuristic alignment, not a morphological gold standard. Tests lock 市場, 学生, 食べる, 本.

## Glosses

1. Lexicon `data/gloss/{ru,ja}_en.json` keyed by lemma (Russian lookup is case-insensitive).
2. Remaining lemmas: one-shot LLM batch (`gloss_lemmas`), temperature 0, JSON object lemma→1–5 word English gloss. Russian keys lowercased. Failure → empty dict; those tokens stay unglossed.
3. Live `POST /gloss` without a matching passage token does **not** call the LLM; lexicon only.

## Validators

Rules live in JSON. Python only scores. Lemma flags are truncated to **12** so the correction prompt stays readable.

### Severity (to pick the closer draft)

```
len(flags)
+ overlevel_lemma_rate * 10
+ forbidden_case_rate * 20
+ forbidden_tense_rate * 20
+ forbidden_pos_rate * 30
+ subordinate_rate * 8
```

Lower is better.

### Russian (`validator.py` + `data/grammar/ru_cefr.json`)

Checked against pymorphy tags: allowed cases and tenses, forbidden POS (participles, verbal adverbs, comparatives), forbidden conjunctions, subordinate-clause rate, over-level lemma rate.

Sentence-initial **когда** is treated as “when (time)”, not a subordinate conjunction.

A1 also skips likely proper names when scoring unknown lemmas (capitalized non-initial nouns).

A draft **passes** only if all of these hold:

- case / tense / POS / subordinate rates ≤ caps in JSON
- over-level content-lemma rate ≤ cap
- **zero** forbidden-conjunction hits (`conj_hits == 0`)

| Level | Grammar (simplified) |
| ----- | -------------------- |
| **A1** | Nominative + present only. No subordinates. No participles / gerunds / comparatives. Caps: over-level 0.15, forbidden case 0.12, tense 0.12, POS 0.02, subordinate 0. |
| **A2** | Nom, acc, gen, prep, dat. Present / past / future. *когда / если / потому* allowed sparingly (subordinate cap 0.08). No instrumental, no *который*, no *бы*. |
| **B1** | All six cases. Aspect contrast, motion verbs, reflexives, imperatives. Simple subordinates (cap 0.28). Still no participles / gerunds / *бы* / *который*. Forbidden case/tense caps 0. |
| **B2** | Full case system. Participles, verbal adverbs, *бы*, *который*-clauses allowed. Vocab still capped (over-level 0.30). POS cap 1.0 (effectively off). |

Content POS for over-level and learner counts: `NOUN, ADJF, ADJS, VERB, INFN, ADVB, PRED, NUMR`.

### Japanese (`validator_ja.py` + `data/grammar/ja_cefr.json`)

Constructions are detected from Sudachi tokens (particles, auxiliaries, inflection form), not from the LLM’s opinion.

| Flag | Detection |
| ---- | --------- |
| `te_form` | surface て / で and POS particle |
| `te_iru` | that て/で followed by lemma いる / おる |
| `plain_past` | lemma た / だ as aux, not after ます / です |
| `plain_neg` | lemma ない as aux, not after ます / です |
| `conditional` | lemma ば / たら / なら, or form starts with 仮定形 |
| `potential` / `passive` | lemma れる / られる (both flags fire; the JSON decides which is forbidden) |
| `causative` | lemma させる / せる |
| `relative` | form starts with 連体形, token is a verb, next word is a noun |
| `keigo` | lemma in a closed list: いらっしゃる, おっしゃる, なさる, くださる, いたす, 申す, 申し上げる, ございます, いただく, 差し上げる, 拝見, 承知 |

A1 also forbids lemmas such as ば, たら, なら, ながら, のに, ように, わけ, はず, べき.

**Any** hit on a forbidden construction or forbidden lemma fails the draft (`conj_hits == 0` required). Over-level lemma rate and POS rate still have caps. Case/tense rates are unused (stored 0; JSON caps are 1.0).

Unknown content lemmas count as over-level. The skip for “names” only fires when the surface is capitalized — rare in Japanese — so loanwords in katakana often count as unknown.

| Level | Allowed (simplified) |
| ----- | -------------------- |
| **A1** | です/ます only. Core particles. No て-form, plain past/neg, ている, conditionals, potential, causative, passive, relatives, keigo. Over-level cap 0.18. |
| **A2** | て-form, てください, plain た / ない. Still no ている, conditionals, potential, causative, passive, relatives, keigo. Over-level 0.20. |
| **B1** | ている, potential, causative, simple relatives, ば/たら/なら. No passive-as-voice, no keigo. Over-level 0.22, subordinate cap 0.28. |
| **B2** | Passive and modest keigo allowed. Vocab aimed at B2 / N3–N2. Over-level 0.30. |

Content POS for over-level and learner counts: `noun, verb, i-adj, na-adj, adverb`.

## Lexicons

| File | Size (approx.) | Purpose |
| ---- | -------------- | ------- |
| `data/vocab/ru_cefr.json` | ~5,400 lemmas | Lemma → A1–B2. Pedagogical core plus frequency banding from a 50k word list |
| `data/vocab/ja_cefr.json` | ~500 lemmas | Pedagogical Japanese core, dictionary form |
| `data/gloss/ru_en.json` | ~1,360 | Short English glosses (not every frequency lemma has a gloss) |
| `data/gloss/ja_en.json` | ~500 | Short English glosses, keyed to Sudachi dictionary form |
| `data/grammar/ru_cefr.json` | 4 levels | Allowed cases/tenses, forbidden POS/conjunctions, rate caps, prompt text |
| `data/grammar/ja_cefr.json` | 4 levels | Forbidden constructions/lemmas, rate caps, prompt text |
| `data/kanji/ja.json` | ~13,100 | Character → on, kun, meanings |

Russian vocab bands are TORFL-inspired pedagogical assignments plus frequency ranks (top ~500 → A1, ~1500 A2, ~3000 B1, rest of the kept list B2). They are **not** a licensed official word list. Japanese is a curated N5–N3-ish core, not JLPT official lists.

`data/raw/` is gitignored. Rebuild:

```
python3 scripts/build_ja_lexicon.py
python3 scripts/build_lexicon.py   # needs pymorphy3; optionally data/raw/ru_50k.txt
```

Grammar JSON is edited by hand.

## Translation

`translate_passage` asks for natural English with the same paragraph breaks, temperature 0.2. Failure or missing key → `null`. `ensure_translation` fills a stored empty column on first `GET …/translation`.

## Known NLP failure modes

- pymorphy3 first-parse can be the wrong lemma or case; the validator then flags or misses it.
- Sudachi mode C still splits in ways that confuse て+いる and relative-clause detection.
- `れる/られる` is tagged as both potential and passive; B1 forbids `passive` so potential られる can false-fail B1.
- Japanese construction detection will both over- and under-flag (heuristic).
- Soft fail means the shelf can contain texts that are harder than their label; the reader warning is the only UI for that.
