# Design specifications

Levla is meant to feel like a **small printed reader**, not a language-app dashboard. Paper, ink, one accent, long reading measure, almost no chrome.

Implementation lives in `frontend/src/app/globals.css`, `layout.tsx`, the shared components (`band.tsx`, `segmented.tsx`, `passage-article.tsx`, `gloss-card.tsx`, `generation-progress.tsx`, `seal.tsx`), the screens (`shelf.tsx`, `reader.tsx`, `generate-form.tsx`), and the landing page (`components/landing/*`). There is no component library, no dark mode, no illustrations. The exam seal is the one brand object; it is not an illustration of a character.

## Rationale for the 2026 redesign

Three departures from the earlier spec, and why.

1. **A landing page now exists at `/`; the shelf moved to `/library`.** The old spec forbade a marketing page. The product claim (CEFR as a *checked* constraint, not a prompt adjective) is invisible from the shelf, so a visitor never learned why this is different from asking a chatbot for "A2 Japanese". The landing page states the claim, shows the analyzer's flags on a prompted draft next to a checked one, and runs the real reader on a hand-authored passage. Nothing on it is a mockup: the hero uses the same `PassageArticle` and `GlossCard` as `/passage/[id]`.
2. **Hairlines replace boxes.** The shelf list, words list, reader toolbar, and gloss kanji list are rules between rows rather than bordered cards. Cards remain for exactly two things: the inverted Continue block and the raised proof sheets. This is the main move away from a "SaaS card grid" and toward a printed page.
3. **CEFR bands are drawn as a joined strip.** Wherever a level *matters* (placement, reader header, the demo), the four bands are shown as one hairline box with the current band inked (`BandStrip`). Where a level is only metadata (a shelf row), it is plain serif text. Inside the gloss card the band is a single hairline chip. No coloured badges.

Kept on purpose: the palette, the two typefaces, ink-on-paper inversion as the only emphasis, no icons beyond typographic arrows, no page transitions.

## Brand

| | |
| --- | --- |
| Name | **Levla** |
| Document title | `Levla — graded readers` (`%s · Levla` on inner pages) |
| One-liner (metadata) | CEFR-calibrated Russian and Japanese passages. The level is checked by a morphological analyzer, not promised by a prompt. Tap any word for lemma, grammar, and a gloss. |
| Landing headline | Graded readers where A2 is actually A2. |
| Kicker | `Russian · Japanese · A1–B2` |
| Library kicker | `{Language} · Library` |

Copy is short, second-person, and specific. No gamification ("streak", "XP"), no creature mascot, no exclamation marks in chrome. Numbers are set tabular (`tnum`). The only brand object is the **exam seal** (`seal.tsx`): one double-ring stamp for every language, terracotta ink, inscription from `SEAL_COPY`. It never appears in the gloss. Adding a language is a copy row (`script`, pass word, fail word), not a new drawing. Missing languages fall back to PASS / FAIL.

## Color

CSS custom properties on `:root`, registered as Tailwind theme colors (`bg-paper`, `text-ink`, `border-rule`, `text-terracotta`, …).

| Token | Hex | Role |
| ----- | --- | ---- |
| `--paper` | `#f3eee4` | Page background |
| `--paper-raised` | `#faf6ee` | Proof sheets, gloss panel, segmented controls, row hover |
| `--paper-deep` | `#eae3d4` | Hover wash inside segmented controls. A tonal step of paper, not a second accent |
| `--ink` | `#1b1712` | Text, inverted blocks, primary button, active band |
| `--rule` | `#d7cbb8` | Every hairline, skeleton bars |
| `--terracotta` | `#b84a2a` | Kicker, selected genre chip, errors, selected word wash, drift flags on the landing page |

Grammar-colour inks (`--g-*`) are unchanged and remain an opt-in overlay.

Derived states use opacity modifiers, not extra tokens: `text-ink/70 /55 /50 /45 /40`, `hover:bg-paper-raised`, `bg-terracotta/16` (selected word), `border-terracotta/30 bg-terracotta/10` (error panel).

Terracotta appears on the landing page on the kicker, the underlines and flags on the drifted draft, its "would fail" summary line, and the exam seals on both proof sheets. The checked draft’s type is ink only; the pass seal is the terracotta on that sheet.

## Typography

Google fonts via `next/font` in `layout.tsx`.

| Role | Face | Notes |
| ---- | ---- | ----- |
| UI / Japanese | **Outfit** (`--font-outfit`) | Latin only; Japanese glyphs come from the system Gothic stack (`.font-ja`) |
| Serif | **Literata** (`--font-literata`) | Variable, `latin` + `cyrillic`, with the **`opsz` axis enabled**. `font-optical-sizing: auto` lets one file set 11 px band labels and 64 px display |
| Morph line | `font-mono` | Grammar tags in the gloss card |

Type roles are `@utility` classes in `globals.css`, so the scale lives in one place:

| Class | Use | Setting |
| ----- | --- | ------- |
| `t-display` | Landing h1, closing line | Literata 450, tracking −0.024em, leading 1.02, balanced |
| `t-heading` | Section h2, library placement line | Literata 450, tracking −0.016em, leading 1.14 |
| `t-kicker` | Brand kicker | Literata 13 px, caps, tracking 0.28em, terracotta |
| `t-eyebrow` | Section labels, field legends, topic line | 11 px, caps, tracking 0.18em, ink/50 |
| `t-folio` | "01", "02" on the landing page | Literata 13 px, tabular |
| `t-quiet` | Text actions (← Library, Restock, toggles) | 13 px, ink/50 → ink on hover |

Sizes in use: landing h1 `2.9 / 3.6 / 4rem`; section h2 `1.9 / 2.4rem`; library placement `2 / 2.5rem`; reader title `2.1 / 2.6rem`; reader body `1.35 / 1.45rem` at leading 1.85 (2.35 with furigana); gloss surface `1.75rem`; landing lede `1.125 / 1.2rem`.

## Layout

Single column everywhere except the landing page.

| Surface | Max width | Padding |
| ------- | --------- | ------- |
| Landing | `max-w-[74rem]`, 12-col grid at `lg` | `px-5 sm:px-8 lg:px-12` |
| Library | `max-w-[36rem]` | `px-5 pt-8 pb-24` / `sm:px-8 sm:pt-10` |
| Reader | `max-w-[42rem]` | `px-5 pt-7 pb-32` / `sm:px-8 sm:pt-9` |
| Review | `max-w-[36rem]` | as library |
| 404 | `max-w-md` | `px-5 py-24` |

Landing sections are separated by a full-width hairline and a folio (`01 The claim`, `02 The loop`, `03 Who it's for`) in a 4 + 8 column split. Section spacing is `mt-28 sm:mt-36`.

## Spacing and radii

Vertical stacks on the app screens use gaps of **3 / 9 / 12** (12 / 36 / 48 px). Form fields are `gap-9`. Row lists are hairline-divided with `py-3.5`.

| Element | Radius |
| ------- | ------ |
| Cards, segmented controls, buttons, gloss panel | `rounded-card` (6 px) |
| Band strip | 4 px |
| Genre chips, feedback pills | `rounded-full` |
| Clickable word | 3 px |
| Kanji stroke diagram | none (hairline square) |
| Inputs | none: `field-line` is a bottom rule only |

## Controls

- **Segmented** (`segmented.tsx`): one hairline box divided into cells; the active cell inverts to ink. Used for language (shelf header, demo) and CEFR level (restock form).
- **BandStrip / BandChip** (`band.tsx`): see rationale above.
- **Primary button** (`btn-primary`): 48 px, ink fill, paper text, 6 px radius. One per screen at most.
- **Toggles** (reader, demo): underlined 13 px text; pressed = ink text with a stronger underline. `aria-pressed` is set.
- **Focus**: a global `:focus-visible` outline, 1.5 px ink, 3 px offset.

## Iconography and motion

No icons. Typographic arrows only (`←`, `→`, `↓`). Transitions are colour and border, 150 ms. `prefers-reduced-motion` collapses them. No page transitions, no skeleton shimmer.

Three animated elements, all paced rather than decorative:

1. The **generation progress hairline** (`generation-progress.tsx`): a 1 px rule that fills asymptotically (never past 94 %) while five stages (Writing at A2 → Analyzing every word → Scoring → Rewriting if it missed → Stamping {level}) move from ink/30 to ink on a timer, with an elapsed-seconds count. It is a paced account of what the backend does, not a measured one, and the copy says "Usually 20–40 seconds". When the job returns, the hairline completes, the fifth stage is the active one, and the exam seal presses before navigation.
2. **Kanji stroke order** (`stroke-order.tsx`): when a Japanese word opens in the gloss, each kanji shows a KanjiVG diagram immediately. Faint traces of the character sit under ink strokes that draw in sequence, with numbers appearing as each stroke starts. Click the diagram to replay. `prefers-reduced-motion` shows the completed numbered diagram with no drawing.
3. The **exam seal** (`seal.tsx`): one press, scale 1.16 → 1 with a few degrees of rotation, 280 ms. `prefers-reduced-motion` shows the seal already down. On inverted surfaces (Continue) the seal uses paper instead of terracotta.

The gloss panel keeps its soft upward shadow on `sm+` because it floats.

## Screens

### Landing (`/`)

1. Nav: wordmark, anchor links (The check, The loop), **Library →**.
2. Hero: kicker, headline, lede, **Open the library**, and the **reader demo** (`reader-demo.tsx`): a raised proof sheet with a band strip, language segmented control, title, Grammar / Furigana toggles, the passage as clickable words, and the gloss area beneath. One word is preselected on load (`食べ` / `продавцу`) so the gloss is visible immediately. Sample passages live in `demo-data.ts` in the real `Token` shape.
3. **01 The claim**: two proof sheets (`drift.tsx`). Left, a prompted draft with the analyzer's flags marked in terracotta (`ている · B1`, `keigo · B2`, …) and "4 constructions above A2 · would fail", with a fail exam seal pressed into the sheet. Right, the checked draft in an ink-bordered sheet with its report (over-level lemmas, banned constructions, flags caught), a pass seal, and "passes A2". Below, the four-step procedure (Constrain, Analyze, Score, Rewrite).
4. **02 The loop**: five numbered steps; step three shows the feedback pills, step four two band strips (A2 → B1).
5. **03 Who it's for**: For / Not.
6. Close: "Pick a passage." and the button again. Footer: Levla · Morphology by Sudachi and pymorphy3 · A single-user demo.

The whole page follows one language choice (the demo's segmented control).

### Library (`/library`)

1. Header: wordmark (links to `/`), language segmented control (hidden when only Japanese is enabled).
2. Kicker `{Language} · Library`, heading **Your {Language} is at {band}.**, band strip, status line (`{n} lemmas seen.` / `Rate a passage to move it.` + `Three ratings in a row move the band.`).
3. Auth panel (only when the backend requires it): hairline-bounded row or email form.
4. Error panel.
5. **Continue**: the inverted card. Topic and chapter top-left, inverted band strip and a mark-size exam seal top-right, title, meta line, **Read →**.
6. Review row (only when cards are due).
7. **The shelf**: hairline rows. Title, band + chapter right-aligned in serif, then `{topic} · {n} words · {n}% new · audio · read`. Hover washes the row to paper-raised. A mark-size fail seal sits on rows that failed calibration; passed rows stay unmarked.
8. **Words**: hairline rows with Remove; lemma, gloss, source title; export links. Stroke-order diagrams stay off this list — they belong on review.
9. **Restock**: a section label and **Restock the shelf →**; open state shows one sentence and the form, with **Hide restock** below. **Review saved words** sits beside it when nothing is due.

### Restock form

Language and level are segmented controls (level cells: serif band + hint). Topic is a `field-line` input. Genre stays as terracotta-selected pills. Submit is `btn-primary`, full width, then the generation progress block under a hairline while busy. Quota line under the button when known. When the job returns, the fifth stage (“Stamping {level}”) activates, the exam seal presses with the real `calibration.passed` verdict, and navigation waits ~900 ms (or a **Read →** click). `prefers-reduced-motion` skips the wait.

### Reader (`/passage/[id]`)

Header: **← Library** left; tracked meta (`{n} words · {n} new · {n} known`, `sm+`) and a band strip right.

Topic line as eyebrow (`{topic} · chapter n · {n}% new`), then the title, with a corner exam seal on the title block. The seal’s verdict is `calibration.passed` (pass inscription or fail), even if the passage is still readable. Audio bar if present.

Toolbar: a hairline-bounded row. Left, toggles **English · Sentence · Grammar · Furigana (ja) · Known**. Right, **Why this is {band}** which opens the calibration report as a definition list inside the same row, with a smaller seal on that report. Legend appears under the toggles when Grammar is on.

Article rules are unchanged (word buttons, hover, selection, chain highlight, fade known, furigana). Calibration warnings print with a terracotta left rule.

The **English** block sits under the passage with an eyebrow. Full translation and **Sentence** share that block: Sentence turns off the gloss and fills the same English section with the tapped sentence. In Sentence mode the article selects whole sentences (hover and click), not individual words.

Sticky bottom bar and gloss panel behave as before. The gloss floats at `min(38rem, 100% − 2rem)` on `sm+`, up to `75vh`. Unselected feedback pills dim after a rating; **Read next →** sits at the right of the status line.

### Review, 404, loading

Review follows the library header pattern (`← Library`, due count as tracked meta). Japanese cards show stroke-order diagrams only after **Show**, together with the gloss and ratings. 404 links **Back to the library**. The reader loading state is a static composition: header with `← Library` and an empty band-strip outline, a title bar, a toolbar of three stubs, and five text lines.

## Gloss card content order

Unchanged: surface (with reading beside it) → lemma + band chip → morph line → suffix chain → gloss → Save → kanji rows (hairline-divided). Each kanji row opens with its stroke-order diagram already playing; tap the diagram to replay.

## Interaction rules

Unchanged from the previous spec (`levla.language`, `levla.grammar`, `levla.furigana`, `levla.fade`, `levla.device_id`; abort on language change; one-shot feedback; lazy English). The demo on the landing page keeps its own local state and never calls the API. Post-sign-in redirects land on `/library`. The service worker precaches `/`, `/library`, `/review`; the PWA `start_url` is `/library`.

## Accessibility

- Gloss panel: `role="dialog"`, close button labelled. Demo gloss area: `role="region"`, `aria-live="polite"`.
- Word buttons and toggles set `aria-pressed`. Segmented controls are `radiogroup` / `radio`. Kanji stroke diagrams in the gloss, and on review after **Show**, are buttons labelled to replay stroke order. Exam seals are `role="img"` with the inscription and band as the label.
- Global `:focus-visible` ring.
- Band strips carry an `aria-label` (`A2 on a scale of A1 to B2`).
- `text-ink/40` remains the weakest tone and should not carry essential meaning alone.

## What not to add

- Dark mode, gradients, drop shadows on cards, coloured CEFR badges, progress rings, creature mascots, testimonials, pricing.
- A third typeface, or a second accent.
- A second seal geometry per language, a face or speech bubble on the seal, or the seal inside the gloss card.
- Anything on the landing page that is not the real product: no illustration of the reader, only the reader.
