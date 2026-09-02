# Prompt for Claude Fable — Levla visual redesign + landing page

> Copy everything below into Fable as one message. It's written to be self-contained: it includes the product, the current design system, and what to change.

---

I want you to redesign the visual design of my app, **Levla**, and design a **landing page** for it (one doesn't exist yet — right now the app opens straight into the logged-out shelf). I want the whole thing to feel genuinely premium and considered — not a generic SaaS template, not "AI app" chrome. Treat this as a real design pass, not a reskin: push on typography, spacing, and detail the way a small, well-funded studio would for a paid product.

## What Levla is

Levla is a CEFR-calibrated graded reader for Russian and Japanese (A1–B2). It generates short reading passages constrained to a checkable CEFR level, validated by a morphological analyzer, then serves them through a reader where the learner taps any word for lemma, grammar, and gloss. After each passage the learner rates it too easy / just right / too hard, which updates their placement and picks the next passage. It's a single-user demo — no accounts, no billing, no sync.

The core differentiator, and the thing the landing page needs to sell: CEFR level here is a **checked constraint**, not a prompt adjective. Most "AI-generated A2 Japanese" drifts into grammar way above the stated level. Levla generates against the level, then runs a real morphological analyzer against the output before it's shown to anyone.

Two screens today: the **shelf** (library + placement + restock) and the **reader** (passage + word-level gloss + grammar coloring + furigana + feedback). Full behavioral spec is below if you need it, but the redesign is about look, not new functionality.

## The current design system (context, not a hard spec)

The existing app is intentionally spare: a "small printed reader," not a dashboard.

- **Palette:** warm paper background (`#f3eee4`), near-black ink (`#1b1712`), a single terracotta accent (`#b84a2a`), a soft rule/border tone (`#d7cbb8`). No dark mode, no gradients, no drop shadows, no colored status badges.
- **Type:** Outfit for UI chrome and Japanese; Literata (latin + cyrillic) for the wordmark, Russian reading text, and CEFR labels. No third typeface.
- **Signature move:** ink-on-paper inversion (filled dark card/chip) is the *only* emphasis treatment — used for the recommended "Continue" card and the active language/level pill.
- **Restraint as a feature:** no icons except a plain "←", no mascots, no gamification language ("streak," "XP"), no page-transition animation.

I'm not precious about any of this — you can propose changing colors, type, or the whole system if it makes the product feel better. But I do want you to treat the **quiet, print-like, unbranded-AI-product feeling** as the thing to protect or deliberately improve on, not something to accidentally lose by defaulting to typical AI-app polish (soft shadows, gradient blobs, rounded-everything SaaS look). If you keep the existing palette, take it further — better rhythm, better contrast, better use of the terracotta as a genuinely rare accent. If you change it, tell me why and keep the same discipline: one accent, restrained motion, no dashboard-ification.

## What "super nice" means here

- Typography that's doing real work — a confident type scale, real optical rhythm, not just "make the heading bigger."
- Generous, deliberate whitespace. The existing spacing rhythm (gaps of 8/12/32/40px) is a reasonable starting point but push it further if the landing page needs more room to breathe.
- Small details that read as craft: how CEFR bands are shown, how the gloss card looks, hover states on the clickable words in the reader, the loading state for passage generation (which takes 20–40s and currently just shows static bars).
- Nothing that reads as an AI-generated template — no default rounded cards with soft shadows and a gradient hero, no stock hero illustration, no generic "AI-powered" iconography.

## The landing page specifically

There isn't one today — the app currently skips straight to the logged-in-feeling shelf. Design a real landing page that:

- Leads with the actual claim: CEFR level as a checked constraint, not a prompt adjective — make this concrete and legible, not marketing fluff. A short before/after or "what drifts vs. what's checked" moment would land well if you can make it visual without turning into a dashboard.
- Shows the reader experience itself (tap a word → lemma/grammar/gloss) as the hero moment, since that's the actual product, not an abstract illustration.
- Explains the loop in as few words as possible: pick a passage → read, tap words → rate it → placement adjusts → next passage.
- States plainly what it's for (serious hobbyists and heritage learners of Russian or Japanese who've outgrown textbook dialogues and don't trust "AI-generated A2") and what it's not (no accounts, no SRS, no C1/C2, not a general language app).
- Ends in one clear action into the shelf. No pricing, no testimonials, no fake logos — this is a demo, not a funded startup.

## Deliverables

1. A landing page design (as a real page, not a mockup image) that could sit at `/`, with the current shelf moving to something like `/library`.
2. An updated look for the shelf and reader screens consistent with whatever system you land on for the landing page — I don't want the landing page to feel like a different product from the app.
3. A short written rationale for any major departures from the current system (palette, type, or the "no landing page" stance in the old spec — I'm intentionally overriding that one now).

## Full current behavior, for reference (don't redesign functionality, just use this so nothing gets lost)

[Paste the full contents of [design.md](http://design.md) and [product.md](http://product.md) here before sending — leaving them out of this prompt to keep it focused, but Fable will need them for accurate detail like the gloss card content order, grammar-color legend, sticky bottom bar states, etc.]

---

*Note: I wrote "don't redesign functionality" above on purpose — I want the visual language and the landing page, not new features or flows.*