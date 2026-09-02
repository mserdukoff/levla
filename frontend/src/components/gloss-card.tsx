"use client";

import { BandChip } from "@/components/band";
import {
  jaGrammarLine,
  morphLine,
  type ConjPiece,
  type KanjiPart,
  type LangCode,
  type Token,
} from "@/lib/types";

function gradeLabel(grade: number): string {
  if (grade >= 1 && grade <= 6) return `grade ${grade}`;
  if (grade === 7 || grade === 8) return "junior high";
  if (grade === 9 || grade === 10) return "names";
  return `grade ${grade}`;
}

function kanjiFacts(part: KanjiPart): string {
  const bits: string[] = [];
  if (part.jlpt) bits.push(`N${part.jlpt}`);
  if (part.grade) bits.push(gradeLabel(part.grade));
  if (part.strokes) bits.push(`${part.strokes} strokes`);
  if (part.freq) bits.push(`freq ${part.freq}`);
  return bits.join(" · ");
}

function readingLine(items: string[], cap = 6): string {
  const clean = items.filter(Boolean);
  if (clean.length <= cap) return clean.join(" · ");
  return `${clean.slice(0, cap).join(" · ")}…`;
}

function KanjiList({ parts }: { parts: KanjiPart[] }) {
  return (
    <ul className="mt-4 flex flex-col divide-y divide-rule border-t border-rule">
      {parts.map((part, i) => {
        const on = readingLine(part.on, 6);
        const kun = readingLine(part.kun, 6);
        const facts = kanjiFacts(part);
        const nanori = readingLine(part.nanori ?? [], 6);
        const components = (part.parts ?? []).filter(
          (p) => p && p !== part.char && p !== part.radical,
        );
        return (
          <li key={`${part.char}-${i}`} className="flex items-start gap-4 py-3">
            <span className="font-ja w-9 shrink-0 text-[1.75rem] leading-none text-ink">
              {part.char}
            </span>
            <div className="flex min-w-0 flex-col gap-1">
              <p className="flex flex-wrap items-baseline gap-x-2">
                {part.reading ? (
                  <span className="font-ja text-sm text-ink/55">{part.reading}</span>
                ) : null}
                {part.meaning ? (
                  <span className="text-sm text-ink/85">{part.meaning}</span>
                ) : null}
              </p>
              {on || kun ? (
                <p className="text-[12px] leading-snug text-ink/50">
                  {on ? (
                    <>
                      <span className="text-[10px] uppercase tracking-[0.14em] text-ink/40">
                        on{" "}
                      </span>
                      <span className="font-ja">{on}</span>
                    </>
                  ) : null}
                  {on && kun ? <span className="text-ink/25"> · </span> : null}
                  {kun ? (
                    <>
                      <span className="text-[10px] uppercase tracking-[0.14em] text-ink/40">
                        kun{" "}
                      </span>
                      <span className="font-ja">{kun}</span>
                    </>
                  ) : null}
                </p>
              ) : null}
              {facts ? (
                <p className="tnum text-[10px] uppercase tracking-[0.14em] text-ink/40">
                  {facts}
                </p>
              ) : null}
              {part.radical || components.length > 0 ? (
                <p className="text-[12px] text-ink/45">
                  {part.radical ? (
                    <>
                      <span className="font-ja">{part.radical}</span>
                      {part.radical_name ? ` ${part.radical_name}` : ""}
                    </>
                  ) : null}
                  {part.radical && components.length > 0 ? (
                    <span className="mx-1.5 text-ink/25">·</span>
                  ) : null}
                  {components.length > 0 ? (
                    <span className="font-ja">{components.join(" ")}</span>
                  ) : null}
                </p>
              ) : null}
              {nanori ? (
                <p className="text-[12px] text-ink/40">
                  <span className="text-[10px] uppercase tracking-[0.14em]">names </span>
                  <span className="font-ja">{nanori}</span>
                </p>
              ) : null}
            </div>
          </li>
        );
      })}
    </ul>
  );
}

function ConjBreakdown({ pieces, language }: { pieces: ConjPiece[]; language: LangCode }) {
  if (pieces.length < 2) return null;
  const jp = language === "ja" ? "font-ja" : "font-reading";
  return (
    <ul className="mt-2.5 flex flex-wrap gap-x-4 gap-y-2">
      {pieces.map((piece, i) => {
        const color = piece.label === "stem" ? "text-g-verb" : "text-g-aux";
        return (
          <li key={`${piece.text}-${piece.label}-${i}`} className="flex flex-col">
            <span className={`${jp} text-[1.2rem] leading-tight ${color}`}>{piece.text}</span>
            <span className="mt-0.5 text-[10px] uppercase tracking-[0.14em] text-ink/40">
              {piece.label}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

/**
 * Word gloss. Content order is fixed by the spec:
 * surface → reading → lemma + band → morph line → suffix chain → gloss → save → kanji.
 */
export function GlossCard({
  token,
  language,
  saved,
  saving,
  onToggleSave,
  maxHeight = true,
}: {
  token: Token;
  language: LangCode;
  saved: boolean;
  saving: boolean;
  onToggleSave: () => void;
  maxHeight?: boolean;
}) {
  const morph = token.morph;
  const line = morph ? morphLine(morph) : "";
  const ja = language === "ja";
  const jaLine = ja ? jaGrammarLine(token) : "";
  const kanji = token.kanji ?? [];
  const conj = token.conj ?? [];
  const showLemma = Boolean(token.lemma && token.lemma !== token.text);
  const jp = ja ? "font-ja" : "font-reading";
  return (
    <div className={`flex flex-col overflow-y-auto pr-1 ${maxHeight ? "max-h-[60vh]" : ""}`}>
      <p className="flex flex-wrap items-baseline gap-x-3">
        <span className={`${jp} text-[1.75rem] leading-tight text-ink`}>{token.text}</span>
        {morph?.reading ? (
          <span className={`${ja ? "font-ja" : ""} text-sm text-ink/50`}>{morph.reading}</span>
        ) : null}
      </p>
      {showLemma || token.level ? (
        <p className="mt-1.5 flex flex-wrap items-center gap-x-2.5 text-sm text-ink/70">
          {showLemma ? (
            <span className={`font-medium text-ink ${jp}`}>{token.lemma}</span>
          ) : null}
          {token.level ? <BandChip level={token.level} /> : null}
        </p>
      ) : null}
      {!ja && line ? (
        <p className="mt-1.5 font-mono text-[12px] tracking-wide text-ink/50">{line}</p>
      ) : null}
      {ja && jaLine ? (
        <p className="mt-1.5 font-mono text-[12px] tracking-wide text-ink/50">{jaLine}</p>
      ) : null}
      {ja ? <ConjBreakdown pieces={conj} language={language} /> : null}
      <p className="mt-3 text-[1.0625rem] leading-snug text-ink/90">
        {token.gloss ?? "No gloss for this lemma yet."}
      </p>
      {token.lemma ? (
        <button
          type="button"
          disabled={saving}
          onClick={onToggleSave}
          className={`mt-3 self-start text-[13px] tracking-[0.02em] underline decoration-ink/20 underline-offset-4 transition-colors hover:text-ink disabled:opacity-50 ${
            saved ? "text-ink decoration-ink/40" : "text-ink/50"
          }`}
        >
          {saved ? "Saved" : "Save"}
        </button>
      ) : null}
      {kanji.length > 0 ? <KanjiList parts={kanji} /> : null}
    </div>
  );
}
