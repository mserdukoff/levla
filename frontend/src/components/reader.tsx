"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { BandStrip } from "@/components/band";
import { GlossCard } from "@/components/gloss-card";
import { GrammarLegend, PassageArticle } from "@/components/passage-article";
import { Seal } from "@/components/seal";
import { fetchPassageStats, fetchTranslation, sendFeedback, starWord, unstarWord } from "@/lib/api";
import {
  loadFadeKnown,
  loadFurigana,
  loadGrammarColors,
  saveFadeKnown,
  saveFurigana,
  saveGrammarColors,
} from "@/lib/device";
import { sentenceEnglish, tokenSentenceIndex } from "@/lib/sentences";
import type { FeedbackRating, Passage, PassageStats } from "@/lib/types";

const LANG_NAME = { ja: "Japanese", ru: "Russian" } as const;

function Toggle({
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

function GrammarPassport({ passage, open }: { passage: Passage; open: boolean }) {
  if (!open) return null;
  const cal = passage.calibration;
  const allowed = cal.allowed_constructions ?? [];
  const banned = cal.banned_constructions ?? [];
  const used = cal.forbidden_used ?? [];
  const rows: { k: string; v: string }[] = [
    {
      k: "Over-level lemmas",
      v: `${Math.round(cal.overlevel_lemma_rate * 100)}%${
        cal.sample_lemmas && cal.sample_lemmas.length > 0
          ? ` · sample: ${cal.sample_lemmas.join(" · ")}`
          : ""
      }`,
    },
  ];
  if (allowed.length > 0) rows.push({ k: `Allowed at ${passage.level}`, v: allowed.join(", ") });
  if (banned.length > 0) rows.push({ k: `Banned at ${passage.level}`, v: banned.join(", ") });
  rows.push({
    k: "Flags caught",
    v: used.length > 0 ? used.join(", ") : "none",
  });
  return (
    <div className="relative mt-5 border-t border-rule pt-5">
      <div className="pointer-events-none absolute right-0 top-5">
        <Seal
          verdict={cal.passed ? "pass" : "fail"}
          language={passage.language}
          level={passage.level}
          size="mark"
        />
      </div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 pr-12 text-sm">
        {rows.map((row) => (
          <div key={row.k} className="contents">
            <dt className="t-eyebrow pt-[3px]">{row.k}</dt>
            <dd className="tnum leading-relaxed text-ink/70">{row.v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function AudioBar({
  passage,
  activeSentence,
  onSentence,
}: {
  passage: Passage;
  activeSentence: number | null;
  onSentence: (index: number | null) => void;
}) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const cues = passage.audio_cues ?? [];
  if (!passage.audio_url) return null;

  function onTime() {
    const audio = audioRef.current;
    if (!audio || cues.length === 0) return;
    const ms = audio.currentTime * 1000;
    const hit = cues.find((c) => ms >= c.start_ms && ms < c.end_ms);
    onSentence(hit ? hit.index : null);
  }

  return (
    <div className="mt-6 flex flex-col gap-2">
      <audio
        ref={audioRef}
        src={passage.audio_url}
        controls
        preload="none"
        className="w-full"
        onTimeUpdate={onTime}
        onPause={() => onSentence(null)}
        onEnded={() => onSentence(null)}
      />
      {activeSentence != null ? (
        <p className="tnum text-[13px] text-ink/45">Line {activeSentence + 1}</p>
      ) : null}
    </div>
  );
}

const FEEDBACK: { id: FeedbackRating; label: string }[] = [
  { id: "too_easy", label: "Too easy" },
  { id: "just_right", label: "Just right" },
  { id: "too_hard", label: "Too hard" },
];

export function Reader({ passage }: { passage: Passage }) {
  const [selected, setSelected] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<FeedbackRating | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [stats, setStats] = useState<PassageStats | null>(null);
  const [nextId, setNextId] = useState<string | null>(null);
  const [placement, setPlacement] = useState<string | null>(null);
  const [showEnglish, setShowEnglish] = useState(false);
  const [showSentence, setShowSentence] = useState(false);
  const [english, setEnglish] = useState<string | null>(passage.translation ?? null);
  const [englishLoading, setEnglishLoading] = useState(false);
  const [englishError, setEnglishError] = useState<string | null>(null);
  const [grammarColors, setGrammarColors] = useState(false);
  const [furigana, setFurigana] = useState(false);
  const [fadeKnown, setFadeKnown] = useState(true);
  const [starred, setStarred] = useState<Set<string>>(new Set());
  const [savingWord, setSavingWord] = useState(false);
  const [audioSentence, setAudioSentence] = useState<number | null>(null);
  const [passportOpen, setPassportOpen] = useState(false);
  const sentenceIds = useMemo(
    () => tokenSentenceIndex(passage.tokens, passage.language),
    [passage.tokens, passage.language],
  );

  const ja = passage.language === "ja";
  const font = ja ? "font-ja" : "font-reading";
  const selectedToken = selected != null ? passage.tokens[selected] : null;

  useEffect(() => {
    setGrammarColors(loadGrammarColors());
    setFurigana(loadFurigana());
    setFadeKnown(loadFadeKnown());
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetchPassageStats(passage.id)
      .then((data) => {
        if (cancelled) return;
        setStats(data);
        setNextId(data.next_id);
        setPlacement(data.placement);
        setStarred(new Set(data.starred_lemmas ?? []));
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
    setShowSentence(false);
    setEnglish(passage.translation ?? null);
    setEnglishLoading(false);
    setEnglishError(null);
    setAudioSentence(null);
    setSelected(null);
    setFeedback(null);
    setPassportOpen(false);
  }, [passage.id, passage.translation]);

  async function onFeedback(rating: FeedbackRating) {
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
              known_lemmas: prev.known_lemmas,
            }
          : prev,
      );
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : "Could not save feedback.");
    } finally {
      setSending(false);
    }
  }

  function onToggleGrammar() {
    setGrammarColors((prev) => {
      const next = !prev;
      saveGrammarColors(next);
      return next;
    });
  }

  function onToggleFurigana() {
    setFurigana((prev) => {
      const next = !prev;
      saveFurigana(next);
      return next;
    });
  }

  function onToggleFade() {
    setFadeKnown((prev) => {
      const next = !prev;
      saveFadeKnown(next);
      return next;
    });
  }

  async function ensureEnglish(): Promise<string | null> {
    if (english) return english;
    setEnglishLoading(true);
    setEnglishError(null);
    try {
      const text = await fetchTranslation(passage.id);
      setEnglish(text);
      return text;
    } catch (err) {
      setEnglishError(err instanceof Error ? err.message : "Could not load the translation.");
      return null;
    } finally {
      setEnglishLoading(false);
    }
  }

  async function onToggleEnglish() {
    if (showEnglish) {
      setShowEnglish(false);
      return;
    }
    setShowSentence(false);
    setShowEnglish(true);
    await ensureEnglish();
  }

  async function onToggleSentence() {
    if (showSentence) {
      setShowSentence(false);
      return;
    }
    setShowEnglish(false);
    setShowSentence(true);
    await ensureEnglish();
  }

  async function onToggleSave() {
    const lemma = selectedToken?.lemma;
    if (!lemma) return;
    setSavingWord(true);
    try {
      if (starred.has(lemma)) {
        await unstarWord(lemma, passage.language);
        setStarred((prev) => {
          const next = new Set(prev);
          next.delete(lemma);
          return next;
        });
      } else {
        await starWord({
          lemma,
          gloss: selectedToken.gloss,
          passage_id: passage.id,
          language: passage.language,
        });
        setStarred((prev) => new Set(prev).add(lemma));
      }
    } catch {
      /* keep current saved state */
    } finally {
      setSavingWord(false);
    }
  }

  const lemmaTotal = stats ? stats.new_lemmas + stats.recycled_lemmas : 0;
  const newPct = lemmaTotal > 0 ? Math.round(((stats?.new_lemmas ?? 0) / lemmaTotal) * 100) : null;
  const glossOpen = Boolean(selectedToken?.is_word && !showSentence);
  const focusSentence =
    showSentence && selected != null ? (sentenceIds[selected] ?? null) : null;
  const sentenceCaption =
    showSentence && selected != null
      ? englishLoading
        ? "Loading English…"
        : englishError
          ? englishError
          : (sentenceEnglish(passage.tokens, passage.language, selected, english) ??
            "No English for this sentence yet.")
      : null;

  return (
    <div
      className={`mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pt-7 sm:px-8 sm:pt-9 ${
        glossOpen ? "pb-[min(40rem,80vh)]" : "pb-32"
      }`}
    >
      <header className="flex items-center justify-between gap-4">
        <Link href="/library" className="t-quiet">
          ← Library
        </Link>
        <div className="flex items-center gap-3">
          <span className="tnum hidden text-[11px] uppercase tracking-[0.16em] text-ink/45 sm:inline">
            {passage.word_count} words
            {lemmaTotal > 0 ? ` · ${stats?.new_lemmas} new · ${stats?.recycled_lemmas} known` : ""}
          </span>
          <BandStrip level={passage.level} />
        </div>
      </header>

      <div className="relative mt-12 pr-[6.5rem] sm:mt-14 sm:pr-[7.5rem]">
        <p className="t-eyebrow">
          {passage.topic}
          {newPct != null ? ` · ${newPct}% new` : ""}
        </p>
        <h1
          className={`mt-3 text-[2.1rem] leading-[1.15] tracking-[-0.01em] text-ink sm:text-[2.6rem] ${font}`}
        >
          {passage.title}
        </h1>
        <div className="pointer-events-none absolute -right-1 top-0 sm:right-0">
          <Seal
            verdict={passage.calibration.passed ? "pass" : "fail"}
            language={passage.language}
            level={passage.level}
            size="corner"
            animate
          />
        </div>
      </div>

      <AudioBar passage={passage} activeSentence={audioSentence} onSentence={setAudioSentence} />

      <div className="mt-8 border-y border-rule py-3">
        <div className="flex flex-wrap items-baseline justify-between gap-x-5 gap-y-2">
          <div className="flex flex-wrap items-baseline gap-x-5 gap-y-2">
            <Toggle on={showEnglish} onClick={onToggleEnglish}>
              English
            </Toggle>
            <Toggle on={showSentence} onClick={onToggleSentence}>
              Sentence
            </Toggle>
            <Toggle on={grammarColors} onClick={onToggleGrammar}>
              Grammar
            </Toggle>
            {ja ? (
              <Toggle on={furigana} onClick={onToggleFurigana}>
                Furigana
              </Toggle>
            ) : null}
            <Toggle on={fadeKnown} onClick={onToggleFade}>
              Known
            </Toggle>
          </div>
          <Toggle on={passportOpen} onClick={() => setPassportOpen((v) => !v)}>
            Why this is {passage.level}
          </Toggle>
        </div>
        {grammarColors ? <GrammarLegend language={passage.language} className="mt-3" /> : null}
        <GrammarPassport passage={passage} open={passportOpen} />
      </div>

      <PassageArticle
        tokens={passage.tokens}
        language={passage.language}
        selected={selected}
        onSelect={setSelected}
        grammarColors={grammarColors}
        furigana={furigana}
        fadeKnown={fadeKnown}
        knownLemmas={stats?.known_lemmas ?? []}
        sentenceIds={sentenceIds}
        audioSentence={audioSentence}
        focusSentence={focusSentence}
        sentenceMode={showSentence}
        className="mt-10 text-[1.35rem] sm:text-[1.45rem]"
      />

      {showEnglish || (showSentence && sentenceCaption) ? (
        <div className="mt-12 border-t border-rule pt-8">
          <p className="t-eyebrow mb-4">English</p>
          {englishLoading ? (
            <p className="text-sm text-ink/45">Loading English…</p>
          ) : englishError ? (
            <p className="text-sm text-terracotta">{englishError}</p>
          ) : showEnglish && english ? (
            <p className="whitespace-pre-wrap font-reading text-[1.05rem] leading-[1.7] text-ink/75">
              {english}
            </p>
          ) : (
            <p className="whitespace-pre-wrap font-reading text-[1.05rem] leading-[1.7] text-ink/75">
              {sentenceCaption}
            </p>
          )}
        </div>
      ) : null}

      {passage.calibration.warnings.length > 0 ? (
        <p className="mt-10 border-l-2 border-terracotta/40 pl-3 text-xs leading-relaxed text-ink/50">
          {passage.calibration.warnings.join(" ")}
        </p>
      ) : null}

      {glossOpen && selectedToken?.is_word ? (
        <div
          className="fixed inset-x-0 bottom-0 z-20 border-t border-rule bg-paper-raised px-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] pt-5 shadow-[0_-8px_30px_rgba(27,23,18,0.08)] sm:inset-x-auto sm:bottom-6 sm:left-1/2 sm:w-[min(38rem,calc(100%-2rem))] sm:-translate-x-1/2 sm:rounded-card sm:border sm:px-8 sm:pb-7 sm:pt-6"
          role="dialog"
          aria-label="Word gloss"
        >
          <div className="mx-auto flex max-w-[42rem] items-start justify-between gap-4 sm:max-w-none">
            <GlossCard
              token={selectedToken}
              language={passage.language}
              saved={Boolean(selectedToken.lemma && starred.has(selectedToken.lemma))}
              saving={savingWord}
              onToggleSave={onToggleSave}
            />
            <button
              type="button"
              onClick={() => setSelected(null)}
              className="t-quiet shrink-0"
              aria-label="Close gloss"
            >
              Close
            </button>
          </div>
        </div>
      ) : (
        <footer className="fixed inset-x-0 bottom-0 z-10 border-t border-rule bg-paper/95 px-5 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 backdrop-blur-sm">
          <div className="mx-auto flex max-w-[42rem] items-center justify-between gap-3">
            <p className="hidden text-[13px] text-ink/45 sm:block">
              Was this {passage.level} passage…
            </p>
            <p className="text-[13px] text-ink/45 sm:hidden">This passage was</p>
            <div className="flex flex-wrap justify-end gap-2">
              {FEEDBACK.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  disabled={sending || Boolean(feedback)}
                  onClick={() => onFeedback(item.id)}
                  className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors disabled:cursor-default ${
                    feedback === item.id
                      ? "border-ink bg-ink text-paper"
                      : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                  } ${feedback && feedback !== item.id ? "opacity-50" : ""}`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          {feedbackError ? (
            <p className="mx-auto mt-2 max-w-[42rem] text-xs text-terracotta">{feedbackError}</p>
          ) : null}
          {feedback && !feedbackError ? (
            <p className="mx-auto mt-2 flex max-w-[42rem] items-baseline justify-between gap-3 text-xs text-ink/50">
              <span>
                {placement
                  ? `Saved. Your ${LANG_NAME[passage.language]} is at ${placement}.`
                  : "Saved."}
              </span>
              {nextId ? (
                <Link
                  href={`/passage/${nextId}`}
                  className="text-[13px] text-ink underline decoration-ink/30 underline-offset-4"
                >
                  Read next →
                </Link>
              ) : null}
            </p>
          ) : null}
        </footer>
      )}
    </div>
  );
}
