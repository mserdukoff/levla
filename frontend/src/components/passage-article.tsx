"use client";

import { furiganaReading, isContentWord, type LangCode, type Token } from "@/lib/types";

export const ROLE_TEXT: Record<string, string> = {
  topic: "text-g-topic",
  subject: "text-g-subject",
  object: "text-g-object",
  particle: "text-g-particle",
  verb: "text-g-verb",
  aux: "text-g-aux",
  adj: "text-g-adj",
  adverb: "text-g-adverb",
};

const JA_LEGEND: { swatch?: string; label: string; role: string }[] = [
  { swatch: "は", label: "topic", role: "topic" },
  { swatch: "が", label: "subject", role: "subject" },
  { swatch: "を", label: "object", role: "object" },
  { label: "particle", role: "particle" },
  { label: "verb", role: "verb" },
  { label: "ending", role: "aux" },
  { label: "adjective", role: "adj" },
];

const RU_LEGEND: { label: string; role: string }[] = [
  { label: "verb", role: "verb" },
  { label: "adjective", role: "adj" },
  { label: "preposition", role: "particle" },
  { label: "adverb", role: "adverb" },
];

export function GrammarLegend({ language, className = "" }: { language: LangCode; className?: string }) {
  const items = language === "ja" ? JA_LEGEND : RU_LEGEND;
  return (
    <p
      className={`flex flex-wrap items-baseline gap-x-3.5 gap-y-1 text-[11px] uppercase tracking-[0.12em] text-ink/40 ${className}`}
    >
      {items.map((item) => (
        <span key={item.role + item.label} className={ROLE_TEXT[item.role]}>
          {"swatch" in item && typeof item.swatch === "string" ? (
            <span className="font-ja normal-case tracking-normal">{item.swatch} </span>
          ) : null}
          {item.label}
        </span>
      ))}
    </p>
  );
}

/**
 * The passage itself: every word is a button. Shared by the reader and the
 * landing-page demo so the hero shows the real thing.
 */
export function PassageArticle({
  tokens,
  language,
  selected,
  onSelect,
  grammarColors = false,
  furigana = false,
  fadeKnown = false,
  knownLemmas = [],
  sentenceIds,
  audioSentence = null,
  className = "",
}: {
  tokens: Token[];
  language: LangCode;
  selected: number | null;
  onSelect: (index: number | null) => void;
  grammarColors?: boolean;
  furigana?: boolean;
  fadeKnown?: boolean;
  knownLemmas?: string[];
  sentenceIds?: number[];
  audioSentence?: number | null;
  className?: string;
}) {
  const ja = language === "ja";
  const selectedToken = selected != null ? tokens[selected] : null;
  const selectedConjId = selectedToken?.conj_id != null ? selectedToken.conj_id : null;
  const rubyOn = furigana && ja;
  return (
    <article
      lang={ja ? "ja" : "ru"}
      className={`text-ink ${rubyOn ? "leading-[2.35]" : "leading-[1.85]"} ${
        ja ? "font-ja" : "font-reading"
      } ${className}`}
    >
      {tokens.map((token, i) => {
        if (!token.is_word) {
          return (
            <span key={i}>
              {token.text}
              {token.ws}
            </span>
          );
        }
        const isOn = selected === i;
        const inChain =
          selectedConjId != null && token.conj_id != null && token.conj_id === selectedConjId;
        const roleCls = grammarColors && token.role ? ROLE_TEXT[token.role] : "";
        const faded =
          fadeKnown &&
          knownLemmas.length > 0 &&
          isContentWord(token, language) &&
          Boolean(token.lemma && knownLemmas.includes(token.lemma));
        const reading = furigana ? furiganaReading(token) : null;
        const liveLine =
          audioSentence != null && sentenceIds != null && sentenceIds[i] === audioSentence;
        const colorCls = roleCls || (faded && !grammarColors ? "text-ink/40" : "text-ink");
        const fadeCls = faded && grammarColors ? "opacity-40" : "";
        const lineCls = liveLine ? "bg-terracotta/12" : "";
        return (
          <span key={i}>
            <button
              type="button"
              onClick={() => onSelect(isOn ? null : i)}
              aria-pressed={isOn}
              className={`word ${colorCls} ${fadeCls} ${lineCls} ${
                isOn ? "word-on" : inChain ? "word-chain" : ""
              }`}
            >
              {reading ? (
                <ruby>
                  {token.text}
                  <rt>{reading}</rt>
                </ruby>
              ) : (
                token.text
              )}
            </button>
            {token.ws}
          </span>
        );
      })}
    </article>
  );
}
