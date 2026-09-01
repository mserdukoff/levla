# Design specifications

Levla is meant to feel like a **small printed reader**, not a language-app dashboard. Paper, ink, one accent, long reading measure, almost no chrome.

Implementation lives in `frontend/src/app/globals.css`, `layout.tsx`, and the three components (`shelf.tsx`, `reader.tsx`, `generate-form.tsx`). There is no component library, no dark mode, no illustrations.

## Brand

| | |
| --- | --- |
| Name | **Levla** |
| Document title | `Levla — graded readers` |
| One-liner (metadata) | CEFR-calibrated Russian and Japanese passages. Click any word for lemma, grammar, and a gloss. |
| Shelf kicker | `Russian · Japanese · A1–B2` |
| Shelf subtitle | Graded readers at a real CEFR level. Pick a text. Too easy or too hard moves the next one. |

Copy is short, second-person, and specific. No gamification (“streak”, “XP”), no mascot, no exclamation marks in chrome.

## Color

CSS custom properties on `:root`, also registered as Tailwind theme colors (`bg-paper`, `text-ink`, `border-rule`, `text-terracotta`, …).

| Token | Hex | Role |
| ----- | --- | ---- |
| `--paper` | `#f3eee4` | Page background |
| `--paper-raised` | `#faf6ee` | Cards, inputs, gloss sheet, unselected chips |
| `--ink` | `#1b1712` | Body text, selected chips, primary buttons, recommended card |
| `--rule` | `#d7cbb8` | Borders, skeleton bars, hairlines |
| `--terracotta` | `#b84a2a` | Brand kicker, selected genre chips, errors, 404 link, text selection |

Optional **grammar-colour** inks, used only when the reader Grammar toggle is on. They are pedagogical overlays, not brand accents. Nouns stay `--ink`.

| Token | Hex | Role |
| --- | --- | --- |
| `--g-topic` | `#b84a2a` | は (topic); same ink as terracotta |
| `--g-subject` | `#2c6b73` | が (subject) |
| `--g-object` | `#8b5420` | を (object) |
| `--g-particle` | `#3f4a28` | other particles; Russian prepositions |
| `--g-verb` | `#3d3a78` | verbs |
| `--g-aux` | `#7a3d5c` | endings (ます / た / て / です) |
| `--g-adj` | `#2a5a45` | adjectives |
| `--g-adverb` | `#6a5340` | adverbs |

Derived states (Tailwind opacity modifiers, not extra tokens):

| Use | Recipe |
| --- | ------ |
| Secondary text | `text-ink/70`, `/55`, `/50`, `/45`, `/40` |
| Placeholder | `placeholder:text-ink/30` |
| Hover border | `hover:border-ink/30` |
| Word hover wash | `hover:bg-ink/8` |
| Selected word | `bg-terracotta/18` |
| Error panel | `border-terracotta/30 bg-terracotta/10 text-terracotta` |
| Word underline (idle) | `decoration-ink/15` |
| Word underline (hover) | `decoration-ink/40` |
| Text selection | `color-mix(in srgb, terracotta 28%, transparent)` |

**Ink-on-paper inversion** is the only “emphasis” treatment: the recommended Continue card and the active language/level chip are `bg-ink text-paper`. Genre chips are the exception — selected genre uses terracotta fill, not ink.

Do not introduce a third accent. Do not use pure black or pure white.

## Typography

Google fonts via `next/font` in `layout.tsx`. HTML `lang="en"`; the reading article sets `lang="ja"` or `lang="ru"`.

| Role | Face | Fallback | Used for |
| ---- | ---- | -------- | -------- |
| UI / Japanese | **Outfit** (`--font-outfit`) | `Hiragino Sans`, `Hiragino Kaku Gothic ProN`, `Yu Gothic`, `Noto Sans JP`, system sans | Body chrome, Japanese titles and body (`.font-ja`) |
| Display / Russian reading | **Literata** (`--font-literata`), subsets `latin` + `cyrillic` | `Iowan Old Style`, `Palatino Linotype`, Palatino, serif | Wordmark, CEFR labels on generate, Russian titles and body (`.font-display`, `.font-reading`) |
| Morph line | `font-mono` | system mono | Russian grammar tags in the gloss card (`aspect · tense · case · …`) |

Outfit is loaded with Latin only. Japanese glyphs come from the system Gothic stack, not from the Outfit file.

### Type scale (as implemented)

| Surface | Size / tracking |
| ------- | --------------- |
| Shelf kicker | 13px, uppercase, `tracking-[0.28em]`, terracotta, Literata |
| Wordmark “Levla” | `text-6xl`, medium, `tracking-tight`, Literata |
| Shelf subtitle | `text-lg`, `leading-relaxed`, `text-ink/70` |
| Section labels (Continue, The shelf, Level, Topic, Genre) | 11px, medium, uppercase, `tracking-[0.18em]`, `text-ink/50` |
| Passage card title | `text-lg leading-snug` |
| Card CEFR | 11px uppercase `tracking-[0.14em]` |
| Card meta | 13px |
| Reader title | 1.85rem / sm: 2.15rem, `leading-snug` |
| Reader body | 1.35rem / sm: 1.45rem, `leading-[1.85]` |
| English translation | 1.05rem, `leading-[1.7]`, Literata, `text-ink/75` |
| Gloss surface | `text-2xl` |
| Gloss reading | `text-sm text-ink/50` |
| Calibration warning | `text-xs text-ink/40` |
| 404 title | `text-3xl` Literata |

Antialiased on `<html>`.

## Layout

Single column. No sidebar, no top nav bar, no footer site-wide.

| Surface | Max width | Padding |
| ------- | --------- | ------- |
| Shelf | `max-w-[34rem]` (~544px) | `px-5 py-16` / `sm:px-8` |
| Reader | `max-w-[42rem]` (~672px) | `px-5 pt-8 pb-28` / `sm:px-8` (bottom padding clears the sticky bar) |
| 404 | `max-w-md` | `px-5 py-24` |

Shelf is narrower than the reader on purpose: the library is a list of cards; the reader needs a longer measure.

Breakpoints used: default (mobile) and `sm` (640px). No tablet/desktop-specific layouts beyond padding, type size, and the gloss card becoming a floating panel.

## Spacing rhythm

Vertical stacks use Tailwind gaps of **2 / 3 / 8 / 10** (8 / 12 / 32 / 40px). Section-to-section on the shelf is `gap-10`. Form fields are `gap-8`. Card lists are `gap-2`. Do not collapse these into a denser dashboard.

Radii:

| Element | Radius |
| ------- | ------ |
| Cards, inputs, language/level chips, primary button | `rounded-lg` or `rounded-xl` |
| Genre chips, feedback pills, CEFR header badge | `rounded-full` |
| Clickable word | `rounded-[3px]` |

Borders are 1px `border-rule` unless selected (`border-ink` or `border-terracotta`).

## Iconography and motion

No icons. The only “graphic” is the ← in “← Shelf”. Transitions are color/border only (`transition`). No page transitions, no skeleton shimmer animation (loading bars are static `bg-rule`). Gloss panel uses a soft upward shadow: `shadow-[0_-8px_30px_rgba(27,23,18,0.08)]`.

## Screens

### Shelf

1. Kicker, wordmark, one-sentence pitch.
2. Two language buttons (English label + native name). Active = ink fill.
3. Placement line: `Your Japanese level is A2. Rate a passage to move it.` After reads: `{n} lemmas seen.`
4. Error (if API down): terracotta-tinted panel.
5. **Continue** — recommended card, inverted.
6. **The shelf** — remaining cards, paper-raised.
7. Text button **Restock the shelf** / **Hide restock**. Opens `GenerateForm` in restock mode (language picker hidden; uses the shelf language).

**Passage card**

- Title (Japanese Gothic / Russian Literata)
- CEFR at top-right
- Topic
- `{n} words · {n} new · {n} known · read`

Recommended card inverts to ink. Hover: `border-ink/30` on non-recommended cards. Entire card is a `Link` to `/passage/{id}`.

### Generate / restock form

| Field | Control |
| ----- | ------- |
| Language | 2-up grid (hidden when `restock`) |
| Level | 4-up grid: A1 Beginner, A2 Elementary, B1 Intermediate, B2 Upper-int. Default **A2** |
| Topic | Single-line input, max 200 chars. Placeholder depends on language (“…Kyoto” vs “…Kazan”) |
| Genre | Pill row; toggling the active pill clears genre (`null`). Default `daily_life` |

Submit: full-width `h-12` ink button. Idle label **Add to shelf** (restock) or **Generate passage**. Busy: **Writing and checking level…** plus helper “Constraining grammar to {level}, then validating every word. This usually takes 20–40 seconds.” Empty topic: “Give the passage a topic.”

On success, `router.push(/passage/{id})`. The button stays disabled (`cursor-wait`) until navigation.

### Reader

Header: **← Shelf** left; pill right with `{level} · {n} words · {n} new · {n} known`.

Title, topic, underline buttons on one wrapping row: **English**, **Sentence**, **Grammar**, **Furigana** (Japanese only), **Known**. All optional overlays except English/Sentence which reveal translation. Grammar / Furigana / Known persist (`levla.grammar`, `levla.furigana`, `levla.fade`). English and Sentence are mutually exclusive.

Grammar off is the default (ink on paper). On: coloured function words plus a compact legend (は topic, が subject, を object, particle, verb, ending, adjective).

Furigana: ruby over kanji that have a token reading. Article line-height increases to `leading-[2.35]`.

Known: content-word lemmas already in `learner_lemmas` fade to `text-ink/40` (or 40% opacity when grammar colours are on). Particles and a first-ever shelf (empty seen-set) do not fade.

Article: each `is_word` token is a button. Idle: faint underline. Hover: stronger underline + ink wash. Selected: terracotta wash, underline off. Non-word tokens (punctuation, Japanese 補助記号) render as plain text. Trailing whitespace lives on `token.ws` so Japanese has no extra spaces.

If calibration `warnings` exist, they print below the article in `text-xs text-ink/40`.

**English block** (when revealed): top rule, then translation in Literata. Loading / error states are one line.

**Sentence block** (when revealed): top rule. If no word is selected, “Tap a word to see that sentence in English.” If a word is selected, that sentence’s English only. Japanese/Russian sentences split on `。！？` / `.!?`; English on `.!?` plus space. Paired by index.

**Sticky bottom** — two mutually exclusive modes:

1. **No word selected:** feedback bar. “Was this {level} passage…” (desktop) / “This passage was” (mobile). Pills **Too easy** / **Just right** / **Too hard**. After save, a status line plus **Read next**. The selected pill fills ink. Sending disables all three.
2. **Word selected:** gloss sheet. Mobile: full-bleed bottom sheet with top rule. `sm+`: floating card centered, `min(24rem, calc(100%-2rem))`, 8px off the bottom, rounded, bordered. Max height `60vh` with overflow scroll. **Close** dismisses (tapping the same word also toggles off). **Save** / **Saved** under the gloss marks the lemma on the shelf Words list.

The feedback bar is hidden while a gloss is open so the two do not stack.

### 404

“Passage gone” / “That reader was not found. Generate a new one.” / terracotta **Back to Levla**.

### Loading

Three static rule-colored bars approximating title + body. No spinner.

## Gloss card content order

1. Surface form (2xl)
2. Reading, if any (Japanese hiragana)
3. Lemma (if different from surface) + CEFR band
4. Russian morph line (`aspect · tense · imperative · case · gender · number · pos`) or Japanese grammar line (`topic marker`, `verb`, `case particle`, …)
5. Japanese verb-suffix row, when the token is part of a chain of two or more pieces (`食べ` stem · `まし` polite · `た` past). Stem uses verb ink; endings use aux ink.
6. English gloss, or “No gloss for this lemma yet.”
7. **Save** / **Saved** (lemma only)
8. Kanji list, each row: character · reading used in this word · all English meanings · on (katakana) / kun (okurigana dots, first six if the list is long) · N-level, grade, strokes, newspaper freq · radical + KRADFILE parts · name readings (first six)
   Max height `60vh` with overflow scroll.

`morphLine` in `types.ts` hides POS when a case is present (case already implies a declined form). Mood `impr` is labeled “imperative”. `jaGrammarLine` maps `role` to a short English label (topic marker, case particle, …).

## Interaction rules

- Language preference persists in `localStorage` (`levla.language`). Grammar colours persist as `levla.grammar` (`1` / `0`). Furigana as `levla.furigana`. Fade known as `levla.fade`. Device UUID (`levla.device_id`) is created on first client render.
- Shelf fetch aborts on language change (`AbortController`).
- Feedback is one-shot in the UI: after a rating, that button stays selected and both stay disabled. Reloading the page does not restore the selected pill (no “already rated” fetch).
- English starts from `passage.translation` if present; otherwise the first reveal hits `/translation` and caches the string in component state.
- Generation is intentionally slow; the form must say so rather than showing a generic spinner.

## Accessibility (current)

- Gloss panel: `role="dialog"` `aria-label="Word gloss"`; close has `aria-label="Close gloss"`.
- Generate errors: `role="alert"`.
- Article `lang` matches the passage language.
- Keyboard: native `<button>` / `<Link>` / `<input>`. No custom focus ring token (browser default).
- Word buttons are in-flow, so a long passage is a long tab sequence. There is no skip-to-feedback link.
- Contrast: ink on paper is strong; `text-ink/40` meta and calibration warnings are the weakest and should not carry essential meaning alone (they currently do for warnings).

## What not to add

- Dark mode, gradients, drop shadows on cards, colored CEFR badges (A1 green / B2 red), progress rings, mascots, or a marketing landing page in this app.
- A second typeface beyond Outfit + Literata + system Gothic.
- A generate page that is not the restock disclosure.

The terracotta + paper palette and the inverted Continue card are the visual signature. Keep them. Grammar colours are an opt-in overlay of muted inks; they must not become a third brand accent on the shelf or chrome.
