"use client";

import { useEffect, useState } from "react";
import { Seal } from "@/components/seal";
import type { CefrLevel, LangCode } from "@/lib/types";

type Stage = { at: number; label: string; detail: string };

function stages(level: CefrLevel, language: LangCode): Stage[] {
  const analyzer = language === "ja" ? "Sudachi" : "pymorphy3";
  return [
    {
      at: 0,
      label: `Writing at ${level}`,
      detail: `The prompt carries the ${level} grammar rules and a sample of in-band lemmas.`,
    },
    {
      at: 10,
      label: "Analyzing every word",
      detail:
        language === "ja"
          ? `${analyzer} tokenizes the draft and attaches lemma, reading, and grammar role.`
          : `${analyzer} tags every token with lemma, case, tense, and aspect.`,
    },
    {
      at: 18,
      label: `Scoring against ${level}`,
      detail: "Over-level lemmas and forbidden constructions are counted against the caps.",
    },
    {
      at: 27,
      label: "Rewriting, if it missed",
      detail: "A failing draft goes back with its flags. The closer attempt is kept.",
    },
    {
      at: Number.POSITIVE_INFINITY,
      label: `Stamping ${level}`,
      detail: "The checker presses the verdict onto the page.",
    },
  ];
}

/**
 * Generation takes 20–40 s and the API is a single call, so this is a paced
 * account of what the backend is doing, not a measured one. The hairline
 * approaches but never reaches the end on its own; the stamp finishes it.
 */
export function GenerationProgress({
  level,
  language,
  verdict = null,
  onRead,
}: {
  level: CefrLevel;
  language: LangCode;
  verdict?: "pass" | "fail" | null;
  onRead?: () => void;
}) {
  const [elapsed, setElapsed] = useState(0);
  const stamped = verdict != null;

  useEffect(() => {
    if (stamped) return;
    const start = Date.now();
    const id = window.setInterval(() => setElapsed((Date.now() - start) / 1000), 250);
    return () => window.clearInterval(id);
  }, [stamped]);

  const list = stages(level, language);
  const paced = list.slice(0, -1).reduce((acc, stage, i) => (elapsed >= stage.at ? i : acc), 0);
  const active = stamped ? list.length - 1 : paced;
  const pct = stamped ? 100 : Math.min(94, 100 * (1 - Math.exp(-elapsed / 22)));
  const seconds = Math.floor(elapsed);

  return (
    <div role="status" aria-live="polite" className="flex flex-col gap-6">
      <div className="h-px w-full bg-rule">
        <div
          className="h-px bg-ink transition-[width] duration-300 ease-linear"
          style={{ width: `${pct}%` }}
        />
      </div>
      <ol className="flex flex-col gap-3">
        {list.map((stage, i) => {
          const state = i < active ? "done" : i === active ? "active" : "todo";
          return (
            <li key={stage.label} className="grid grid-cols-[1.5rem_1fr] gap-x-3">
              <span
                className={`tnum font-display text-[11px] leading-6 tracking-[0.1em] ${
                  state === "todo" ? "text-ink/30" : "text-ink/55"
                }`}
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <p
                  className={`text-[15px] leading-6 transition-colors duration-300 ${
                    state === "active"
                      ? "text-ink"
                      : state === "done"
                        ? "text-ink/50"
                        : "text-ink/30"
                  }`}
                >
                  {stage.label}
                </p>
                {state === "active" ? (
                  <p className="mt-0.5 text-[13px] leading-snug text-ink/50">{stage.detail}</p>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
      {stamped ? (
        <div className="flex flex-col items-center gap-4 border-t border-rule pt-6">
          <Seal
            verdict={verdict}
            language={language}
            level={level}
            size="hero"
            animate
          />
          {onRead ? (
            <button type="button" onClick={onRead} className="t-quiet text-ink">
              Read →
            </button>
          ) : null}
        </div>
      ) : (
        <p className="tnum text-[13px] text-ink/45">
          Usually 20–40 seconds · {seconds}s
          {seconds > 45 ? " · Still checking. A rewrite is a second full pass." : ""}
        </p>
      )}
    </div>
  );
}
