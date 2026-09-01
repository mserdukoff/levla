"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchPassageStats, fetchTranslation, sendFeedback, starWord, unstarWord } from "@/lib/api";
import {
  loadFadeKnown,
  loadFurigana,
  loadGrammarColors,
  saveFadeKnown,
  saveFurigana,
  saveGrammarColors,
} from "@/lib/device";
import { sentenceEnglish } from "@/lib/sentences";
import {
  furiganaReading,
  isContentWord,
  jaGrammarLine,
  morphLine,
  type ConjPiece,
  type FeedbackRating,
  type KanjiPart,
  type Passage,
  type PassageStats,
  type Token,
} from "@/lib/types";

const ROLE_TEXT: Record<string, string> = {
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
    <ul className="mt-2 flex flex-col gap-3 border-t border-rule pt-2">
      {parts.map((part, i) => {
        const on = readingLine(part.on, 6);
        const kun = readingLine(part.kun, 6);
        const facts = kanjiFacts(part);
        const nanori = readingLine(part.nanori ?? [], 6);
        const components = (part.parts ?? []).filter(
          (p) => p && p !== part.char && p !== part.radical,
        );
        return (
          <li key={`${part.char}-${i}`} className="flex items-start gap-3">
            <span className="font-ja w-8 shrink-0 text-[1.65rem] leading-none text-ink">
              {part.char}
            </span>
            <div className="flex min-w-0 flex-col gap-0.5">
              {part.reading ? (
                <p className="font-ja text-sm text-ink/55">{part.reading}</p>
              ) : null}
              {part.meaning ? (
                <p className="text-sm text-ink/80">{part.meaning}</p>
              ) : null}
              {on || kun ? (
                <p className="text-[12px] leading-snug text-ink/50">
                  {on ? (
                    <>
                      <span className="text-[11px] uppercase tracking-[0.12em] text-ink/40">
                        on{" "}
                      </span>
                      <span className="font-ja">{on}</span>
                    </>
                  ) : null}
                  {on && kun ? (
                    <span className="text-ink/25"> · </span>
                  ) : null}
                  {kun ? (
                    <>
                      <span className="text-[11px] uppercase tracking-[0.12em] text-ink/40">
                        kun{" "}
                      </span>
                      <span className="font-ja">{kun}</span>
                    </>
                  ) : null}
                </p>
              ) : null}
              {facts ? (
                <p className="text-[11px] uppercase tracking-[0.12em] text-ink/40">
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
                  <span className="text-[11px] uppercase tracking-[0.12em]">
                    names{" "}
                  </span>
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

function ConjBreakdown({
  pieces,
  language,
}: {
  pieces: ConjPiece[];
  language: Passage["language"];
}) {
  if (pieces.length < 2) return null;
  const jp = language === "ja" ? "font-ja" : "font-reading";
  return (
    <ul className="mt-1 flex flex-wrap gap-x-3 gap-y-1.5">
      {pieces.map((piece, i) => {
        const color =
          piece.label === "stem" ? "text-g-verb" : "text-g-aux";
        return (
          <li key={`${piece.text}-${piece.label}-${i}`} className="flex flex-col">
            <span className={`${jp} text-lg leading-tight ${color}`}>
              {piece.text}
            </span>
            <span className="text-[11px] uppercase tracking-[0.12em] text-ink/40">
              {piece.label}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

function GrammarLegend({ language }: { language: Passage["language"] }) {
  const items = language === "ja" ? JA_LEGEND : RU_LEGEND;
  return (
    <p className="mt-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 text-[11px] uppercase tracking-[0.12em] text-ink/40">
      {items.map((item) => (
        <span key={item.role + item.label} className={ROLE_TEXT[item.role]}>
          {"swatch" in item && item.swatch ? (
            <span className="font-ja normal-case tracking-normal">
              {item.swatch}{" "}
            </span>
          ) : null}
          {item.label}
        </span>
      ))}
    </p>
  );
}

function GlossCard({
  token,
  language,
  saved,
  saving,
  onToggleSave,
}: {
  token: Token;
  language: Passage["language"];
  saved: boolean;
  saving: boolean;
  onToggleSave: () => void;
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
    <div className="flex max-h-[60vh] flex-col gap-1.5 overflow-y-auto pr-1">
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
      {ja && jaLine ? (
        <p className="font-mono text-[12px] tracking-wide text-ink/50">{jaLine}</p>
      ) : null}
      {ja ? <ConjBreakdown pieces={conj} language={language} /> : null}
      <p className="text-base text-ink/90">
        {token.gloss ?? "No gloss for this lemma yet."}
      </p>
      {token.lemma ? (
        <button
          type="button"
          disabled={saving}
          onClick={onToggleSave}
          className="mt-1 self-start text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink disabled:opacity-50"
        >
          {saved ? "Saved" : "Save"}
        </button>
      ) : null}
      {kanji.length > 0 ? <KanjiList parts={kanji} /> : null}
    </div>
  );
}

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
  const [fadeKnown, setFadeKnown] = useState(false);
  const [starred, setStarred] = useState<Set<string>>(new Set());
  const [savingWord, setSavingWord] = useState(false);

  const selectedToken =
    selected != null ? passage.tokens[selected] : null;
  const selectedConjId =
    selectedToken?.conj_id != null ? selectedToken.conj_id : null;

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
      setEnglishError(
        err instanceof Error ? err.message : "Could not load the translation.",
      );
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
      <div className="mt-3 flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <button
          type="button"
          onClick={onToggleEnglish}
          className="text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
        >
          {showEnglish ? "Hide English" : "English"}
        </button>
        <button
          type="button"
          onClick={onToggleSentence}
          aria-pressed={showSentence}
          className="text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
        >
          {showSentence ? "Hide sentence" : "Sentence"}
        </button>
        <button
          type="button"
          onClick={onToggleGrammar}
          aria-pressed={grammarColors}
          className="text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
        >
          {grammarColors ? "Hide grammar" : "Grammar"}
        </button>
        {passage.language === "ja" ? (
          <button
            type="button"
            onClick={onToggleFurigana}
            aria-pressed={furigana}
            className="text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
          >
            {furigana ? "Hide furigana" : "Furigana"}
          </button>
        ) : null}
        <button
          type="button"
          onClick={onToggleFade}
          aria-pressed={fadeKnown}
          className="text-[13px] tracking-wide text-ink/50 underline decoration-ink/20 underline-offset-4 transition hover:text-ink"
        >
          {fadeKnown ? "Hide known" : "Known"}
        </button>
      </div>
      {grammarColors ? <GrammarLegend language={passage.language} /> : null}

      <article
        lang={passage.language === "ja" ? "ja" : "ru"}
        className={`mt-10 text-[1.35rem] text-ink sm:text-[1.45rem] ${
          furigana && passage.language === "ja" ? "leading-[2.35]" : "leading-[1.85]"
        } ${passage.language === "ja" ? "font-ja" : "font-reading"}`}
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
          const inChain =
            selectedConjId != null &&
            token.conj_id != null &&
            token.conj_id === selectedConjId;
          const roleCls =
            grammarColors && token.role ? ROLE_TEXT[token.role] : "";
          const knownSet = stats?.known_lemmas ?? [];
          const faded =
            fadeKnown &&
            knownSet.length > 0 &&
            isContentWord(token, passage.language) &&
            Boolean(token.lemma && knownSet.includes(token.lemma));
          const reading = furigana ? furiganaReading(token) : null;
          const colorCls = roleCls || (faded && !grammarColors ? "text-ink/40" : "text-ink");
          const fadeCls = faded && grammarColors ? "opacity-40" : "";
          return (
            <span key={i}>
              <button
                type="button"
                onClick={() => setSelected(isOn ? null : i)}
                className={`cursor-pointer rounded-[3px] px-[1px] transition ${fadeCls} ${
                  isOn
                    ? `bg-terracotta/18 ${colorCls}`
                    : inChain
                      ? `bg-terracotta/8 ${colorCls} hover:bg-ink/8 underline decoration-ink/15 decoration-[1.5px] underline-offset-[5px] hover:decoration-ink/40`
                      : `${colorCls} hover:bg-ink/8 underline decoration-ink/15 decoration-[1.5px] underline-offset-[5px] hover:decoration-ink/40`
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

      {showSentence ? (
        <div className="mt-8 border-t border-rule pt-6">
          {englishLoading ? (
            <p className="text-sm text-ink/45">Loading English…</p>
          ) : englishError ? (
            <p className="text-sm text-terracotta">{englishError}</p>
          ) : selected == null ? (
            <p className="text-sm text-ink/45">Tap a word to see that sentence in English.</p>
          ) : (
            <p className="font-reading text-[1.05rem] leading-[1.7] text-ink/75">
              {sentenceEnglish(
                passage.tokens,
                passage.language,
                selected,
                english,
              ) ?? "No English for this sentence yet."}
            </p>
          )}
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
            <div className="flex flex-wrap justify-end gap-2">
              <button
                type="button"
                disabled={sending || Boolean(feedback)}
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
                disabled={sending || Boolean(feedback)}
                onClick={() => onFeedback("just_right")}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                  feedback === "just_right"
                    ? "border-ink bg-ink text-paper"
                    : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                }`}
              >
                Just right
              </button>
              <button
                type="button"
                disabled={sending || Boolean(feedback)}
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
