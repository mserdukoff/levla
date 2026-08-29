# Implementation Plan: CEFR-Calibrated Graded Reader Generator (Russian v1)

Built on top of Grammario's existing morphological analysis and CEFR-calibration engine.

## 1. Scope the v1 Tightly

**Pick one language first — Russian.** It has the sharpest inflection moat (the case system defeats naive LLM level-control), you already have tagged corpora and morphological analysis for it, and the diaspora/heritage-learner + serious-hobbyist audience is large and active online (r/Russian, r/languagelearning).

**v1 feature set — nothing more:**

- User picks a CEFR level (A1–B2) and a topic or genre
- System generates a short passage (300–800 words) at that level
- Every word is clickable → shows lemma, case/gender/aspect, and a gloss
- A simple "too easy / too hard" feedback button per passage (your first real user-signal loop)

Cut everything else for now: no SRS integration, no audio, no user accounts beyond basic auth, no multi-language. Those are v2+.

## 2. Technical Architecture

Maps cleanly onto your existing FastAPI/async background.

**Backend (FastAPI):**

- `/generate` endpoint: takes level + topic → calls LLM with a constrained generation prompt, then **validates the output through Grammario's own morphological analyzer** rather than trusting the LLM's self-reported level. This validation step is the actual moat — an LLM asked to "write B1 Russian" will drift into B2 case constructions; your analyzer catches that.
- If validation fails (too many out-of-level grammar structures), either regenerate with a corrective prompt or run a simplification pass on flagged sentences.
- `/gloss` endpoint: word-level lookup using your existing tagged-corpus pipeline — lemma, POS, case/number/gender/aspect, short definition.

**Generation strategy — two viable approaches, pick one to start:**

- **A) Prompt-constrained generation** — give the LLM a vocabulary list capped to the target CEFR level plus explicit grammar constraints (e.g., "A2: only present/past tense, nominative/accusative/prepositional cases, no subordinate clauses"), generate, then validate with your analyzer.
- **B) Generate-then-simplify** — generate freely, then use your analyzer to detect over-level structures and run a targeted rewrite pass on just those sentences.

Start with **A** — it's cheaper (one LLM call instead of generate+revise) and your existing CEFR/grammar-structure work from Grammario's Italian/Spanish tagging gives you the constraint lists to build from.

**Model routing:** use a cheaper/faster model for the bulk generation, and only invoke your own analyzer (not a second LLM call) for validation — that keeps per-generation cost near-zero since the validation is your own code, not another API call.

**Frontend:** Keep it minimal — a reading pane with clickable words (a simple React/Next.js app is fine, or even server-rendered if you want to move faster). The clickable-gloss interaction is the core UX; don't over-invest in anything else for v1.

## 3. Data Needed Before Writing Code

- A CEFR-tagged **vocabulary frequency list** for Russian, banded by level (A1/A2/B1/B2). This doesn't need to be original — there are existing frequency dictionaries you can license/adapt as a starting scaffold, then layer your own grammar-structure constraints on top.
- A **grammar-structure-to-CEFR mapping** — which case uses, verb aspects, and syntactic structures belong at which level. Likely already partially built from Grammario's tagged corpora; formalize it into a ruleset your validator can check against.

## 4. Build Order (Suggested 4–6 Week Sprint)


| Week | Focus                                                                                                                                                                                                                           |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Formalize the CEFR grammar-structure ruleset for Russian (reuse Grammario's existing tagging work). Foundation everything else depends on.                                                                                      |
| 2    | Build the `/generate` endpoint with prompt-constrained generation + morphological validator as a pass/fail gate. Get it producing acceptable A2 and B1 passages consistently.                                                   |
| 3    | Build `/gloss` (word-click lookup) using existing analyzer output — should be close to reusable code from Grammario, not new work.                                                                                              |
| 4    | Minimal frontend — reading view, level/topic picker, clickable words, feedback button.                                                                                                                                          |
| 5    | Closed testing with real learners (r/Russian is a good source — post asking for beta testers, don't sell yet). Watch whether "too easy/too hard" feedback matches your CEFR labeling, and where generation drifts out of level. |
| 6    | Fix what testing surfaces, add lightweight auth + a paywall stub, prepare for a soft public launch.                                                                                                                             |


## 5. Validation Before Building More

Don't add languages, audio, or SRS until there's a signal this specific loop works. Look for:

- Testers actually returning for a second/third passage without prompting
- "Too hard" feedback rate low enough that level-calibration is credible (if B1 passages consistently feel like B2, the ruleset needs work before anything else matters)
- Unsolicited "this is useful because X" comments that reveal the actual retained hook (comprehension confidence? the click-gloss? topic novelty?)

## 6. Distribution (Parallel With Weeks 5–6, Not After)

- Post progress/build-in-public updates in r/Russian and r/languagelearning as you go — free calibration feedback from real learners of the exact plateau problem being solved.
- A short demo video or GIF showing the click-to-gloss interaction tends to travel well in these communities because it's visually self-explanatory.
- Don't launch on Product Hunt yet — save that for a second language or a real usage milestone; it's a one-shot audience.

## 7. Monetization Sequencing

- **Free tier:** limited passages/day, no gloss history.
- **Paid ($5–8/mo):** unlimited passages, saved vocabulary from glosses (becomes the retention hook — a personal word list built from what's been clicked), eventually export to Anki.
- Don't build billing until testers have said unprompted they'd pay — Stripe integration is a day's work, not a blocker to defer decisions on.

## 8. Where to Stop and Reassess

If after the 6-week build + 2 weeks of real testers there's no organic return-usage or positive unsolicited feedback, that's the signal to revisit — either the level-calibration isn't differentiated enough to matter to learners, or Russian specifically isn't the easiest wedge (Japanese, with the existing analysis work, is the fallback language to try next). Better to learn that in 8 weeks than 6 months.