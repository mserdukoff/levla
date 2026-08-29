"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchPassageStats, fetchTranslation, sendFeedback } from "@/lib/api";
import { morphLine, type Passage, type PassageStats, type Token } from "@/lib/types";

function GlossCard({
  token,
  language,
}: {
  token: Token;
  language: Passage["language"];
}) {
  const morph = token.morph;
  const line = morph ? morphLine(morph) : "";
  const kanji = token.kanji ?? [];
  const ja = language === "ja";
  const showLemma = Boolean(token.lemma && token.lemma !== token.text);
  const jp = ja ? "font-ja" : "font-reading";
  return (
    <div className="flex max-h-[50vh] flex-col gap-1.5 overflow-y-auto pr-1">
      <p className={`${jp} text-2xl leading-tight text-ink`}>{token.text}</p>
      {morph?.reading ? (
        <p className={`${ja ? "font-ja" : ""} text-sm text-ink/50`}>
          {morph.reading}
        </p>
      ) : null}
      {showLemma || token.level ? (
        <p className="text-sm text-ink/70">
          {showLemma ? (
            <span className={`font-medium text-ink ${ja ? "font-ja" : ""}`}>
              {token.lemma}
            </span>
          ) : null}
          {token.level ? (
            <span className="ml-2 text-[11px] uppercase tracking-wider text-ink/40">
              {token.level}
            </span>
          ) : null}
        </p>
      ) : null}
      {!ja && line ? (
        <p className="font-mono text-[12px] tracking-wide text-ink/50">{line}</p>
      ) : null}
      <p className="text-base text-ink/90">
        {token.gloss ?? "No gloss for this lemma yet."}
      </p>
      {kanji.length > 0 ? (
        <ul className="mt-2 flex flex-col gap-2 border-t border-rule pt-2">
          {kanji.map((part, i) => {
            const fallback = [...part.on, ...part.kun].filter(Boolean).join(" · ");
            return (
              <li key={`${part.char}-${i}`} className="flex items-baseline gap-3">
                <span className="font-ja w-7 shrink-0 text-xl text-ink">{part.char}</span>
                <div className="min-w-0">
                  <p className="font-ja text-sm text-ink/55">
                    {part.reading ?? fallback}
                  </p>
                  {part.meaning ? (
                    <p className="text-sm text-ink/80">{part.meaning}</p>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}

export function Reader({ passage }: { passage: Passage }) {
  const [selected, setSelected] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<"too_easy" | "too_hard" | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [stats, setStats] = useState<PassageStats | null>(null);
  const [nextId, setNextId] = useState<string | null>(null);
  const [placement, setPlacement] = useState<string | null>(null);
  const [showEnglish, setShowEnglish] = useState(false);
  const [english, setEnglish] = useState<string | null>(passage.translation ?? null);
  const [englishLoading, setEnglishLoading] = useState(false);
  const [englishError, setEnglishError] = useState<string | null>(null);

  const selectedToken =
    selected != null ? passage.tokens[selected] : null;

  useEffect(() => {
    let cancelled = false;
    fetchPassageStats(passage.id)
      .then((data) => {
        if (cancelled) return;
        setStats(data);
        setNextId(data.next_id);
        setPlacement(data.placement);
      })
      .catch(() => {
        /* shelf stats are optional on a direct URL */
      });
    return () => {
      cancelled = true;
    };
  }, [passage.id]);

  useEffect(() => {
    setShowEnglish(false);
    setEnglish(passage.translation ?? null);
    setEnglishLoading(false);
    setEnglishError(null);
  }, [passage.id, passage.translation]);

  async function onFeedback(rating: "too_easy" | "too_hard") {
    setSending(true);
    setFeedbackError(null);
    try {
      const result = await sendFeedback(passage.id, rating);
      setFeedback(rating);
      if (result.next_id) setNextId(result.next_id);
      if (result.placement) setPlacement(result.placement);
      setStats((prev) =>
        prev
          ? {
              ...prev,
              new_lemmas: result.new_lemmas,
              recycled_lemmas: result.recycled_lemmas,
              next_id: result.next_id,
              placement: result.placement ?? prev.placement,
              read: true,
            }
          : prev,
      );
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : "Could not save feedback.");
    } finally {
      setSending(false);
    }
  }

  async function onToggleEnglish() {
    if (showEnglish) {
      setShowEnglish(false);
      return;
    }
    setShowEnglish(true);
    if (english) return;
    setEnglishLoading(true);
    setEnglishError(null);
    try {
      const text = await fetchTranslation(passage.id);
      setEnglish(text);
    } catch (err) {
      setEnglishError(
        err instanceof Error ? err.message : "Could not load the translation.",
      );
    } finally {
      setEnglishLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pb-28 pt-8 sm:px-8">
      <header className="mb-10 flex items-center justify-between gap-4">
        <Link
          href="/"
          className="text-[13px] tracking-wide text-ink/50 transition hover:text-ink"
        >
          ← Shelf
        </Link>
        <span className="rounded-full border border-rule px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-[0.16em] text-ink/60">
          {passage.level}
          <span className="mx-1.5 text-ink/25">·</span>
          {passage.word_count} words
          {stats && stats.new_lemmas + stats.recycled_lemmas > 0 ? (
            <>
              <span className="mx-1.5 text-ink/25">·</span>
              {stats.new_lemmas} new
              <span className="mx-1.5 text-ink/25">·</span>
              {stats.recycled_lemmas} known
            </>
          ) : null}
        </span>
      </header>

      <h1
        className={`text-[1.85rem] leading-snug text-ink sm:text-[2.15rem] ${
          passage.language === "ja" ? "font-ja" : "font-reading"
        }`}
      >
        {passage.title}
      </h1>
      <p className="mt-2 text-sm text-ink/45">{passage.topic}</p>
      <button
        type="button"
        onClick={onToggleEnglish}
        className="mt-3 text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
      >
        {showEnglish ? "Hide English" : "English"}
      </button>

      <article
        lang={passage.language === "ja" ? "ja" : "ru"}
        className={`mt-10 text-[1.35rem] leading-[1.85] text-ink sm:text-[1.45rem] ${
          passage.language === "ja" ? "font-ja" : "font-reading"
        }`}
      >
        {passage.tokens.map((token, i) => {
          if (!token.is_word) {
            return (
              <span key={i}>
                {token.text}
                {token.ws}
              </span>
            );
          }
          const isOn = selected === i;
          return (
            <span key={i}>
              <button
                type="button"
                onClick={() => setSelected(isOn ? null : i)}
                className={`cursor-pointer rounded-[3px] px-[1px] transition ${
                  isOn
                    ? "bg-terracotta/18 text-ink"
                    : "hover:bg-ink/8 underline decoration-ink/15 decoration-[1.5px] underline-offset-[5px] hover:decoration-ink/40"
                }`}
              >
                {token.text}
              </button>
              {token.ws}
            </span>
          );
        })}
      </article>

      {showEnglish ? (
        <div className="mt-10 border-t border-rule pt-8">
          {englishLoading ? (
            <p className="text-sm text-ink/45">Loading English…</p>
          ) : englishError ? (
            <p className="text-sm text-terracotta">{englishError}</p>
          ) : english ? (
            <p className="font-reading text-[1.05rem] leading-[1.7] text-ink/75 whitespace-pre-wrap">
              {english}
            </p>
          ) : null}
        </div>
      ) : null}

      {passage.calibration.warnings.length > 0 ? (
        <p className="mt-8 text-xs leading-relaxed text-ink/40">
          {passage.calibration.warnings.join(" ")}
        </p>
      ) : null}

      {selectedToken?.is_word ? (
        <div
          className="fixed inset-x-0 bottom-0 z-20 border-t border-rule bg-paper-raised px-5 py-4 shadow-[0_-8px_30px_rgba(27,23,18,0.08)] sm:inset-x-auto sm:bottom-8 sm:left-1/2 sm:w-[min(24rem,calc(100%-2rem))] sm:-translate-x-1/2 sm:rounded-xl sm:border"
          role="dialog"
          aria-label="Word gloss"
        >
          <div className="mx-auto flex max-w-[42rem] items-start justify-between gap-4 sm:max-w-none">
            <GlossCard token={selectedToken} language={passage.language} />
            <button
              type="button"
              onClick={() => setSelected(null)}
              className="shrink-0 text-sm text-ink/40 hover:text-ink"
              aria-label="Close gloss"
            >
              Close
            </button>
          </div>
        </div>
      ) : (
        <footer className="fixed inset-x-0 bottom-0 z-10 border-t border-rule bg-paper/95 px-5 py-3 backdrop-blur-sm">
          <div className="mx-auto flex max-w-[42rem] items-center justify-between gap-3">
            <p className="hidden text-[13px] text-ink/45 sm:block">
              Was this {passage.level} passage…
            </p>
            <p className="text-[13px] text-ink/45 sm:hidden">This passage was</p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={sending || feedback === "too_easy"}
                onClick={() => onFeedback("too_easy")}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                  feedback === "too_easy"
                    ? "border-ink bg-ink text-paper"
                    : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                }`}
              >
                Too easy
              </button>
              <button
                type="button"
                disabled={sending || feedback === "too_hard"}
                onClick={() => onFeedback("too_hard")}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                  feedback === "too_hard"
                    ? "border-ink bg-ink text-paper"
                    : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                }`}
              >
                Too hard
              </button>
            </div>
          </div>
          {feedbackError ? (
            <p className="mx-auto mt-2 max-w-[42rem] text-xs text-terracotta">
              {feedbackError}
            </p>
          ) : null}
          {feedback && !feedbackError ? (
            <p className="mx-auto mt-2 max-w-[42rem] text-xs text-ink/45">
              {placement
                ? `Saved. Your ${passage.language === "ja" ? "Japanese" : "Russian"} level is ${placement}.`
                : "Saved."}
              {nextId ? (
                <>
                  {" "}
                  <Link href={`/passage/${nextId}`} className="text-ink underline decoration-ink/20">
                    Read next
                  </Link>
                </>
              ) : null}
            </p>
          ) : null}
        </footer>
      )}
    </div>
  );
}
