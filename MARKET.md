# Levla — market feasibility

Can this be sold as a real app to language learners? Assessment of the current product (furigana, grammar coloring, starred words, sentence English, just-right placement) against how people actually study reading. Scores are analyst judgments of the codebase as of September 2026, not measured usage.

---

## Verdict

**Do not sell it yet.**

| | |
| --- | --- |
| Ready to charge | No |
| Current product-market fit | 3 / 10 |
| Technical wedge | High |
| Path to a paid beta | 4–6 months |

Levla is a strong prototype with a real wedge — morphologically checked CEFR, not ChatGPT roleplay. It is not a product people will pay for or return to daily. The brand promise is “this text is actually A2.” Soft fail, a ~26-text shelf, no audio, and progress tied to localStorage will break that promise in the first week.

A paid beta is realistic in 4–6 months if you pick one language, pre-build a library, add accounts and audio, and stop showing failed calibration as a CEFR-banded reader.

**Bottom line:** Feasible as a real app, not as this build. The interesting company is a calibrated extensive-reading shelf with a custom-topic button — a trusted catalog, sound, accounts, and a word list that comes back. The current repo is the engine room for that company. Marketing it now would spend the CEFR claim before the library can support it.

---

## The job learners actually hire

Serious learners do not hire “an LLM that writes a story.” They hire a daily 15-minute extensive-reading session: a text they can mostly understand, a way to look up the rest without breaking flow, sound attached to the writing, and a feeling that yesterday’s words came back today.

LingQ, Satori Reader, Readlang, NHK Web Easy, and Duolingo Stories all sell some slice of that job. ChatGPT sells infinite custom text with zero calibration. Levla only wins if the learner can feel that the next page is easier or harder for a **structural** reason, not because the model felt like it.

| Job | What good looks like | Levla today |
| --- | --- | --- |
| Read at my level | Trust the band; hide junk; i+1 new words | Ruleset is real; soft-fail still shows the badge |
| Understand in flow | Tap, gloss, furigana, sentence English | Strong — this is the best part of the app |
| Hear it | Line-synced audio or at least TTS | Missing. Dealbreaker for Japanese A1–B1 |
| Keep the words | Star → review → Anki; known words fade | Star + fade exist; no review loop |
| Come back tomorrow | Account, streak, unread queue, series | Device UUID dies on a new phone |
| Have enough to read | Hundreds of texts, or cheap custom topics | ~13 per language plus slow generation |

---

## Table-stakes coverage vs. products learners already use

Analyst scores 0–10. Categories are the features that keep a reading app in someone’s daily rotation. Source: current Levla codebase vs. public LingQ, Satori Reader, and ChatGPT behavior. Not survey data.

| Feature | Levla | LingQ | Satori Reader | ChatGPT |
| --- | ---: | ---: | ---: | ---: |
| Level control | 8 | 5 | 8 | 2 |
| Tap-to-gloss | 8 | 9 | 7 | 1 |
| Audio | 0 | 8 | 10 | 3 |
| Library depth | 2 | 9 | 6 | 10 |
| Vocab save | 5 | 9 | 6 | 0 |
| Habit / sync | 2 | 8 | 6 | 1 |
| Mobile | 4 | 8 | 7 | 9 |

Levla leads on level control; it is empty on audio and catalog. ChatGPT wins on volume and loses on trust.

### Competitive notes (detail)

- **LingQ** wins on corpus and unknown-word workflow; it is ugly and level labels are fuzzy. Copy the known/unknown overlay (fade-known is a start) and ignore the rest of the chrome.
- **Satori Reader** wins on audio and editorial quality for Japanese. You will not beat them on stories. Beat them on “make me a text about my commute that is still A2.”
- **Readlang** wins as a browser layer on real web pages. Different job (authentic content). Stay in graded, generated, controlled text.
- **ChatGPT** is the real competitor for restock. The only defense is a visible, checkable grammar passport and a next-text that actually moves. If you cannot show the check, Levla is slower ChatGPT.

---

## Who would even pay

### Japanese hobbyists, A2–B1 — larger checkbook, harder wedge

Largest willingness to pay in consumer language tech. They already buy WaniKani, Bunpro, Satori Reader. They are allergic to unnatural です/ます and missing audio. Levla’s furigana, construction flags, and kanji breakdown are aimed at them — but a ~500-lemma Japanese list is too small, so generated A1/A2 will either be tiny-vocab or constantly over-level. Harder to differentiate vs. Satori and Tadoku. Sharper distribution (r/LearnJapanese, Refold, Discord).

### Russian A1–B2 — smaller market, cleaner proof

Smaller market, weaker paid competitors, and a technical moat beginners can actually feel: ChatGPT A2 Russian still dumps instrumental and participles. Heritage speakers and TORFL students are a reachable niche (r/russian, university classes). The ~5,400-lemma list is far more usable than Japanese. Russian is the cleaner first public language even if Japanese has more buyers.

**Do not launch both.** Dual-language at launch looks impressive on a landing page and dilutes quality. Ship one language until 50 people finish a third text without being asked.

---

## Pitfalls that will kill conversion

| Severity | Pitfall | Why it matters | Fix |
| --- | --- | --- | --- |
| Blocker | Soft-fail still wears the CEFR badge | One A1 text with て-form or instrumental and the whole claim is fake. Learners will compare to ChatGPT and shrug. | Hide or quarantine failed calibration. Show a trust line: “A2 grammar used: て-form yes, ている no.” |
| Blocker | Library is a weekend, not a habit | ~26 authored texts. A motivated learner burns the shelf, then waits 20–40s and pays you for each restock. | Pre-generate 150–300 texts per language offline. Generation becomes a premium “write about X,” not the default loop. |
| Blocker | No audio | Japanese A1–B1 without sound is a non-starter. Reading and listening are the same skill at this stage. | TTS per sentence at minimum (Google / Azure / Eleven). Later, human or cloned audio on the seed library. |
| Blocker | Progress lives in localStorage | New phone, Safari ITP, or “clear site data” wipes placement, seen lemmas, and stars. Nobody pays for that. | Real accounts (email/OAuth) before any paywall. Device ID can stay as a guest mode. |
| High | Japanese lexicon is too thin | ~500 lemmas means most content words are “unknown” to the validator. Generation either fails or cheats. | Grow JA vocab to 2–4k dictionary forms. Align to a public pedagogical list you can defend. |
| High | Stars do not become study | Saving 本 and never seeing it again is a museum, not a product. LingQ’s hook is the word list becoming the next day’s work. | SRS or at least a “review 10 starred words” pass. Anki export is the credibility feature for this audience. |
| High | Placement is a blunt instrument | One “too easy” jumps a whole CEFR band. A bad mood or a lucky text mis-places the learner for days. | Keep just-right. Require 2–3 signals before a band change. Show “new vs known” as the real difficulty, not only A2/B1. |
| High | LLM prose is pedagogically weird | A1 Japanese that repeats 「私は学生です」 is correct and unreadable. Learners want a story, not a drill sheet. | Human-edit the public library. Constrain generation toward narrative (character, goal, ending), then calibrate. |
| Medium | Unit economics of live generation | Write + rewrite + gloss + translate is several LLM calls. Unlimited custom topics at $8/mo loses money if abused. | Cap free generates. Cache by (level, topic hash, language). Prefer a static catalog. |
| Medium | SQLite + no auth is not a SaaS | Fine for a single user. Not fine for 200 concurrent readers or GDPR deletion requests. | Postgres, per-user rows, and a real delete-my-data path before taking cards. |

---

## What is already worth keeping

Do not rebuild the reader. The click-to-gloss loop, furigana, sentence English, grammar coloring, fade-known, kanji alignment, and too-easy / just-right / too-hard queue are the product. The moat is the validator, not the LLM. If you market anything, market that: **the model proposes, morphology disposes.**

**Keep**

- Constrained generate → morph → CEFR flags → rewrite
- Shelf recommendation
- New vs known counts
- Japanese construction detector
- Russian case gate

**Tighten**

- Hard-fail the public shelf
- Expand JA lexicon
- Make stars reviewable
- Sentence-aligned audio
- Trust UI on every text

**Do not add yet**

- More languages
- Teacher accounts
- Streaks-as-gamification
- Social
- A native app

Those are how this becomes Grammario 2 before anyone finishes a second story.

---

## Features that would make people use it

Ordered by “would I open this tomorrow,” not by engineering fun. Phase 0 is the bar for a public beta people might pay $6–8/mo for. Phase 1 is retention. Phase 2 is the moat becoming visible.

### Phase 0 — paywall prerequisite

1. **Accounts and sync.** Email/OAuth. Guest device ID as fallback.
2. **Hard-fail the shelf.** Only passed calibration is “A2.” Failed drafts stay in a lab/debug view.
3. **Pre-build 150+ texts** per launched language (batch generate + human pass on A1–A2). Restock stays premium.
4. **Sentence-level TTS** with highlight. Japanese first if that is the public language.
5. **Japanese lemma list to at least ~2,000**; gloss coverage to match. Document the banding method.
6. **Public beta in one language.** Russian is the cleaner proof; Japanese is the larger checkbook. Pick.

### Phase 1 — retention

7. **Review starred words** (even a crude SM-2). Anki CSV export. Known-fade on by default for new users.
8. **Today’s reading** (one recommended text), words-read lifetime, optional 10-minute goal. No XP theater.
9. **Multi-chapter stories** with the same characters so “read next” is a cliffhanger, not a random A2.
10. **Placement needs 2–3 ratings** to move a band. Surface new-lemma % as the difficulty the user feels.
11. **Installable PWA**, large type control, offline last-opened text. Skip native until ~1k actives.

### Phase 2 — make the moat visible

12. **Grammar passport on every text:** allowed constructions, over-level rate, sample lemmas. This is the ad.
13. **Generate to this learner’s seen set** with a target new-lemma rate (true i+1), not only CEFR band.
14. **Three comprehension questions** or a one-line recall prompt. Difficulty rating alone is not proof they read.

---

## How to sell it (once Phase 0 exists)

Do not position against Duolingo. Position against “I asked ChatGPT for A2 Japanese and I don’t trust it.”

The demo is a 12-second clip: tap a word, see the grammar, mark too hard, the next text is visibly simpler — and a line on the page lists which constructions were banned. That is the only message that is both true and new.

| Channel | Why | What to post |
| --- | --- | --- |
| r/LearnJapanese, r/russian, r/languagelearning | These people already argue about graded readers | GIF of tap-gloss + calibration flags. Ask if A2 feels like A2. Do not sell. |
| Tadoku / extensive-reading Discords | They live the job-to-be-done | Offer a free A2 pack. Watch whether they request chapter 2. |
| Grammario users | Same founder, same NLP taste, already care about trees | “Read a text that uses only the construction you just studied.” Companion, not a second company. |
| University TORFL / JLPT tutors | They need homework that is actually at the band | Shareable read-only links to a passage. Teacher seats later. |

### Monetization after people return

- **Free:** the human-edited library, tap-to-gloss, limited stars.
- **Paid ($6–8/mo, not $15):** custom topics, audio, unlimited stars, Anki export, i+1 restock.

Do not bill until someone asks for more texts unprompted. Stripe is not the bottleneck.

---

## Unit economics (order of magnitude)

Rough gpt-4o-mini costs via OpenRouter. Not a finance model.

| Action | LLM calls | Ballpark cost | Implication |
| --- | --- | --- | --- |
| Read a seeded text | 0 (translation cached) | ~$0 | This must be the default. Catalog is the business. |
| Generate custom topic (pass first try) | 1 write + gloss fill + translate | $0.01–0.04 | Fine as a paid extra. Dangerous as the core loop. |
| Generate that fails and rewrites | 2 writes + gloss + translate | $0.02–0.08 | Cap retries. Prefer picking a stored text. |
| TTS per 400-word Russian text | 0 LLM; cloud TTS | $0.01–0.05 typical | Cache audio on the passage. Never resynthesize per view. |

---

## Kill / continue criteria

Give a closed group (20–40 learners in **one** language) the Phase 0 build for two weeks. Decide from behavior, not from compliments on the UI.

**Continue if**

- ≥40% finish a second text without a nudge.
- “Too hard” on labeled A2 is not the majority (calibration is believable).
- Unsolicited comments name the hook (level, gloss, or next-text — pick one and double down).
- At least a few people ask for more texts or a way to pay.

**Stop or pivot if**

- They generate once, compare to ChatGPT, and leave.
- They say A2 feels like B1 more often than not — the ruleset is the product and it failed.
- They only praise the design. Pretty readers do not retain.
- Custom generation is the only thing they use — you are a thin wrapper on OpenRouter with extra latency.
