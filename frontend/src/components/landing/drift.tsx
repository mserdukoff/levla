"use client";

import { useEffect, useRef, useState } from "react";
import { Seal } from "@/components/seal";
import type { LangCode } from "@/lib/types";
import { DRIFT } from "./demo-data";

function useOnceInView<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setOn(true);
          io.disconnect();
        }
      },
      { threshold: 0.35 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return { ref, on };
}

/**
 * Two proof sheets: what a plain "make it easy" request produces (with the
 * trouble spots marked on the text) and what the same request produces once
 * it's actually held to the level.
 */
export function Drift({ lang }: { lang: LangCode }) {
  const sample = DRIFT[lang];
  const font = lang === "ja" ? "font-ja" : "font-reading";
  const { ref, on } = useOnceInView<HTMLDivElement>();
  return (
    <div ref={ref} className="grid gap-10 lg:grid-cols-2 lg:gap-8">
      <section className="flex flex-col">
        <p className="t-eyebrow">What most reading practice looks like</p>
        <p className="mt-2 text-[15px] leading-relaxed text-ink/60">{sample.prompt}</p>
        <div className="relative mt-6 flex-1">
          <p
            lang={lang}
            className={`h-full rounded-card border border-rule bg-paper-raised px-5 py-6 pr-16 text-[1.15rem] leading-[1.95] text-ink sm:px-6 sm:pr-20 ${font}`}
          >
            {sample.drifted.map((seg, i) =>
              seg.flag ? (
                <span key={i} className="relative inline whitespace-nowrap">
                  <span className="border-b-[1.5px] border-terracotta">{seg.text}</span>
                  <sup className="ml-0.5 font-sans text-[10px] font-medium uppercase tracking-[0.08em] text-terracotta">
                    {seg.flag}
                  </sup>
                </span>
              ) : (
                <span key={i}>{seg.text}</span>
              ),
            )}
          </p>
          <div className="pointer-events-none absolute -right-1 -top-3 sm:-right-3 sm:-top-4">
            <Seal
              verdict="fail"
              language={lang}
              level="A2"
              size="hero"
              animate={on}
            />
          </div>
        </div>
        <p className="tnum mt-4 text-[13px] text-terracotta">{sample.driftedSummary}</p>
      </section>

      <section className="flex flex-col">
        <p className="t-eyebrow">What you get on Levla</p>
        <p className="mt-2 text-[15px] leading-relaxed text-ink/60">
          Same request, same length — but held to what a beginner has actually learned.
        </p>
        <div className="relative mt-6 flex flex-1 flex-col">
          <div className="flex flex-1 flex-col rounded-card border border-ink bg-paper-raised px-5 py-6 pr-16 sm:px-6 sm:pr-20">
            <p lang={lang} className={`text-[1.15rem] leading-[1.95] text-ink ${font}`}>
              {sample.checked}
            </p>
            <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-5 gap-y-1.5 border-t border-rule pt-4 text-[13px]">
              {sample.checkedReport.map((row) => (
                <div key={row.k} className="contents">
                  <dt className="t-eyebrow pt-[3px]">{row.k}</dt>
                  <dd className="tnum leading-relaxed text-ink/70">{row.v}</dd>
                </div>
              ))}
            </dl>
          </div>
          <div className="pointer-events-none absolute -right-1 -top-3 sm:-right-3 sm:-top-4">
            <Seal
              verdict="pass"
              language={lang}
              level="A2"
              size="hero"
              animate={on}
            />
          </div>
        </div>
        <p className="tnum mt-4 text-[13px] text-ink">{sample.checkedSummary}</p>
      </section>
    </div>
  );
}
