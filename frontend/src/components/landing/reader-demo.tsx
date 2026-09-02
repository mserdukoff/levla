"use client";

import { useState } from "react";
import { BandStrip } from "@/components/band";
import { GlossCard } from "@/components/gloss-card";
import { GrammarLegend, PassageArticle } from "@/components/passage-article";
import { Segmented } from "@/components/segmented";
import { LANGUAGES, type LangCode } from "@/lib/types";
import { DEMO } from "./demo-data";

function DemoToggle({
  on,
  onClick,
  children,
}: {
  on: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={on}
      className={`text-[13px] tracking-[0.02em] underline underline-offset-4 transition-colors hover:text-ink ${
        on ? "text-ink decoration-ink/50" : "text-ink/50 decoration-ink/15"
      }`}
    >
      {children}
    </button>
  );
}

/**
 * The hero: the real reader, on a hand-authored passage. Same article and
 * gloss components as /passage/[id]; nothing here is a mockup.
 * Mounted with key={lang} so switching language resets the selection.
 */
export function ReaderDemo({
  lang,
  onLang,
}: {
  lang: LangCode;
  onLang: (next: LangCode) => void;
}) {
  const demo = DEMO[lang];
  const [selected, setSelected] = useState<number | null>(demo.initial);
  const [grammar, setGrammar] = useState(false);
  const [furigana, setFurigana] = useState(false);
  const [saved, setSaved] = useState<Set<string>>(new Set());

  const token = selected != null ? demo.tokens[selected] : null;
  const ja = lang === "ja";

  return (
    <div className="flex flex-col overflow-hidden rounded-card border border-rule bg-paper-raised">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3 border-b border-rule px-5 py-3 sm:px-7">
        <div className="flex items-center gap-3">
          <BandStrip level={demo.level} />
          <span className="t-eyebrow">{demo.genre}</span>
        </div>
        <Segmented
          ariaLabel="Demo language"
          size="sm"
          options={LANGUAGES.map((l) => ({ id: l.id, label: l.label }))}
          value={lang}
          onChange={onLang}
        />
      </div>

      <div className="px-5 pb-7 pt-6 sm:px-7 sm:pt-7">
        <p className="t-eyebrow">{demo.topic}</p>
        <h2 className={`mt-2 text-[1.55rem] leading-snug text-ink ${ja ? "font-ja" : "font-reading"}`}>
          {demo.title}
        </h2>
        <div className="mt-4 flex flex-wrap items-baseline gap-x-5 gap-y-2 border-y border-rule py-2.5">
          <DemoToggle on={grammar} onClick={() => setGrammar((v) => !v)}>
            Grammar
          </DemoToggle>
          {ja ? (
            <DemoToggle on={furigana} onClick={() => setFurigana((v) => !v)}>
              Furigana
            </DemoToggle>
          ) : null}
          <span className="ml-auto text-[13px] text-ink/40">Tap any word</span>
        </div>
        {grammar ? <GrammarLegend language={lang} className="mt-3" /> : null}
        <PassageArticle
          tokens={demo.tokens}
          language={lang}
          selected={selected}
          onSelect={setSelected}
          grammarColors={grammar}
          furigana={furigana}
          className="mt-6 text-[1.2rem] sm:text-[1.3rem]"
        />
      </div>

      <div
        className="min-h-[11rem] border-t border-rule bg-paper px-5 py-5 sm:px-7"
        role="region"
        aria-label="Word gloss"
        aria-live="polite"
      >
        {token && token.is_word ? (
          <div className="flex items-start justify-between gap-4">
            <GlossCard
              token={token}
              language={lang}
              saved={Boolean(token.lemma && saved.has(token.lemma))}
              saving={false}
              maxHeight={false}
              onToggleSave={() => {
                const lemma = token.lemma;
                if (!lemma) return;
                setSaved((prev) => {
                  const next = new Set(prev);
                  if (next.has(lemma)) next.delete(lemma);
                  else next.add(lemma);
                  return next;
                });
              }}
            />
            <button type="button" onClick={() => setSelected(null)} className="t-quiet shrink-0">
              Close
            </button>
          </div>
        ) : (
          <p className="text-sm text-ink/45">
            Tap a word to see what it means, how it's used
            {ja ? ", and every kanji inside it" : ""}.
          </p>
        )}
      </div>
    </div>
  );
}
