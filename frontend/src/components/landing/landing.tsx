"use client";

import Link from "next/link";
import { useState } from "react";
import { BandStrip } from "@/components/band";
import type { LangCode } from "@/lib/types";
import { Drift } from "./drift";
import { ReaderDemo } from "./reader-demo";

const PROCEDURE: { label: string; detail: string }[] = [
  {
    label: "Write for your level",
    detail:
      "Every passage starts from exactly what you’re expected to know at your level — which words, which grammar — not a vague instruction to “keep it easy.”",
  },
  {
    label: "Read it back, word by word",
    detail:
      "The finished passage gets checked the way a strict teacher would: every single word, looking for anything that’s crept in above your level.",
  },
  {
    label: "Hold the line",
    detail:
      "One verb form you haven’t learned yet, one word too many, and the passage doesn’t pass — no matter how good it reads.",
  },
  {
    label: "Try again",
    detail: "A passage that fails gets rewritten and checked again. Only the one that actually fits reaches you.",
  },
];

const LOOP: { label: string; detail: string }[] = [
  { label: "Pick a passage", detail: "One is already picked for you. Or grab any title you like." },
  { label: "Read it. Tap words.", detail: "Meaning, grammar, and pronunciation, right where you’re reading." },
  { label: "Rate it", detail: "Too easy, just right, or too hard. That is the whole interface." },
  { label: "Your level updates", detail: "Say the same thing a few times in a row and it moves. Otherwise it holds." },
  { label: "Read the next one", detail: "Picked for where you are now, remembering what you just learned." },
];

function SectionHead({
  folio,
  eyebrow,
  title,
  lede,
}: {
  folio: string;
  eyebrow: string;
  title: string;
  lede?: string;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-12 lg:gap-8">
      <div className="flex items-baseline gap-4 lg:col-span-4 lg:flex-col lg:gap-3">
        <p className="t-folio">{folio}</p>
        <p className="t-eyebrow">{eyebrow}</p>
      </div>
      <div className="lg:col-span-8">
        <h2 className="t-heading text-[1.9rem] text-ink sm:text-[2.4rem]">{title}</h2>
        {lede ? (
          <p className="mt-6 max-w-[38rem] text-[1.0625rem] leading-[1.65] text-ink/70 sm:text-[1.125rem]">
            {lede}
          </p>
        ) : null}
      </div>
    </div>
  );
}

export function Landing() {
  const [lang, setLang] = useState<LangCode>("ja");

  return (
    <main className="mx-auto w-full max-w-[74rem] px-5 sm:px-8 lg:px-12">
      <header className="flex items-center justify-between py-6 sm:py-7">
        <span className="font-display text-[1.375rem] font-medium tracking-[-0.02em] text-ink">
          Levla
        </span>
        <nav className="flex items-center gap-7">
          <a href="#check" className="t-quiet hidden sm:inline">
            The proof
          </a>
          <a href="#loop" className="t-quiet hidden sm:inline">
            How it works
          </a>
          <Link href="/library" className="t-quiet text-ink">
            Library →
          </Link>
        </nav>
      </header>

      {/* ---------- hero ---------- */}
      <section className="grid gap-12 border-t border-rule pt-12 lg:grid-cols-12 lg:gap-12 lg:pt-16">
        <div className="flex flex-col lg:col-span-5">
          <p className="t-kicker">Russian · Japanese · Beginner to upper-intermediate</p>
          <h1 className="t-display mt-6 text-[2.9rem] text-ink sm:text-[3.6rem] lg:text-[4rem]">
            Reading practice that actually matches what you know.
          </h1>
          <p className="mt-7 max-w-[30rem] text-[1.125rem] leading-[1.6] text-ink/70 sm:text-[1.2rem]">
            Levla writes short stories in Russian and Japanese for exactly where you are, then
            checks every single one before it reaches you, so the grammar never jumps ahead of
            what you’ve actually learned. Tap any word for what it means, how it’s used, and why.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-4">
            <Link href="/library" className="btn-primary">
              Start reading
            </Link>
            <a href="#check" className="t-quiet">
              See how it works ↓
            </a>
          </div>
          <p className="mt-10 text-[13px] leading-relaxed text-ink/45 lg:mt-auto lg:pt-12">
            No account needed. Tell us a passage was too easy or too hard, and the next one adjusts.
          </p>
        </div>
        <div className="lg:col-span-7">
          <ReaderDemo key={lang} lang={lang} onLang={setLang} />
        </div>
      </section>

      {/* ---------- 01 the check ---------- */}
      <section id="check" className="mt-28 scroll-mt-8 border-t border-rule pt-10 sm:mt-36 sm:pt-12">
        <SectionHead
          folio="01"
          eyebrow="The proof"
          title="If we say it’s your level, we mean it."
          lede={
            lang === "ja"
              ? "Ask any AI tool for “easy Japanese” and it quietly slips in grammar you haven’t met yet — a plain form here, an honorific there — until you’re back to guessing instead of reading. We check every passage line by line before you ever see it, so a beginner text actually reads like one."
              : "Ask any AI tool for “easy Russian” and it quietly slips in a case or a verb form you haven’t met yet, until you’re back to guessing instead of reading. We check every passage line by line before you ever see it, so a beginner text actually reads like one."
          }
        />
        <div className="mt-14 sm:mt-16">
          <Drift key={lang} lang={lang} />
        </div>
        <ol className="mt-16 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
          {PROCEDURE.map((step, i) => (
            <li key={step.label} className="border-t border-rule pt-4">
              <p className="t-folio">{String(i + 1).padStart(2, "0")}</p>
              <p className="mt-3 font-display text-[1.25rem] text-ink">{step.label}</p>
              <p className="mt-2 text-[15px] leading-relaxed text-ink/60">{step.detail}</p>
            </li>
          ))}
        </ol>
        <p className="mt-12 max-w-[38rem] text-[15px] leading-relaxed text-ink/60">
          Every passage keeps this report. Open <em className="not-italic text-ink">Why this is A2</em> in the
          reader any time you want to see exactly what it kept out.
        </p>
      </section>

      {/* ---------- 02 the loop ---------- */}
      <section id="loop" className="mt-28 scroll-mt-8 border-t border-rule pt-10 sm:mt-36 sm:pt-12">
        <SectionHead folio="02" eyebrow="How it works" title="Read. Rate. Move up." />
        <ol className="mt-14 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-5 lg:gap-x-6">
          {LOOP.map((step, i) => (
            <li key={step.label} className="border-t border-rule pt-4">
              <p className="t-folio">{String(i + 1).padStart(2, "0")}</p>
              <p className="mt-3 font-display text-[1.25rem] leading-tight text-ink">{step.label}</p>
              <p className="mt-2 text-[15px] leading-relaxed text-ink/60">{step.detail}</p>
              {i === 2 ? (
                <div className="mt-4 flex flex-wrap gap-1.5" aria-hidden="true">
                  {["Too easy", "Just right", "Too hard"].map((label) => (
                    <span
                      key={label}
                      className={`rounded-full border px-2.5 py-1 text-[12px] ${
                        label === "Just right"
                          ? "border-ink bg-ink text-paper"
                          : "border-rule bg-paper-raised text-ink/70"
                      }`}
                    >
                      {label}
                    </span>
                  ))}
                </div>
              ) : null}
              {i === 3 ? (
                <div className="mt-4 flex items-center gap-2.5" aria-hidden="true">
                  <BandStrip level="A2" />
                  <span className="text-ink/35">→</span>
                  <BandStrip level="B1" />
                </div>
              ) : null}
            </li>
          ))}
        </ol>
      </section>

      {/* ---------- 03 who ---------- */}
      <section className="mt-28 border-t border-rule pt-10 sm:mt-36 sm:pt-12">
        <SectionHead folio="03" eyebrow="Who it’s for" title="Past the textbook, not yet at the newspaper." />
        <div className="mt-14 grid gap-10 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-4 lg:col-start-5">
            <p className="t-eyebrow">For</p>
            <p className="mt-4 text-[1.0625rem] leading-[1.65] text-ink/80">
              Serious hobbyists and heritage learners of Russian or Japanese. You have outgrown
              textbook dialogues, native material is still a wall, and you have stopped trusting
              anything labelled “AI-generated A2”.
            </p>
          </div>
          <div className="lg:col-span-4">
            <p className="t-eyebrow">Not</p>
            <ul className="mt-4 flex flex-col divide-y divide-rule border-y border-rule text-[1.0625rem] leading-[1.65] text-ink/80">
              <li className="py-2.5">No accounts, no sync, no billing.</li>
              <li className="py-2.5">No flashcard decks. You read, you rate.</li>
              <li className="py-2.5">Not advanced or fluent-level yet — beginner through upper-intermediate.</li>
              <li className="py-2.5">Not a general language app. Two screens: a shelf and a reader.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* ---------- close ---------- */}
      <section className="mt-28 border-t border-rule pt-14 sm:mt-36 sm:pt-20">
        <div className="grid gap-8 lg:grid-cols-12">
          <div className="lg:col-span-8 lg:col-start-5">
            <h2 className="t-display text-[2.6rem] text-ink sm:text-[3.4rem]">Pick a passage.</h2>
            <p className="mt-6 max-w-[30rem] text-[1.0625rem] leading-[1.65] text-ink/70 sm:text-[1.125rem]">
              Every level already has passages waiting. Ask for one on any topic you like, and
              it’ll go through the same check before it reaches you.
            </p>
            <div className="mt-9">
              <Link href="/library" className="btn-primary">
                Start reading
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="mt-24 flex flex-wrap items-baseline justify-between gap-x-8 gap-y-2 border-t border-rule py-8 text-[13px] text-ink/45 sm:mt-32">
        <span className="font-display text-[15px] text-ink/70">Levla</span>
        <span>Every passage checked before you see it</span>
        <span>A single-user demo</span>
      </footer>
    </main>
  );
}
