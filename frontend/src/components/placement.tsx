"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Art } from "@/components/landing/art";
import { PassageArticle } from "@/components/passage-article";
import { fetchPlacement, submitPlacement } from "@/lib/api";
import { saveLanguage, useStoredLanguage } from "@/lib/device";
import type { LangCode, PlacementRead, PlacementResult } from "@/lib/types";
import { readingFont } from "@/lib/types";

const NAMES = { ja: "Japanese", ru: "Russian", it: "Italian", ar: "Arabic" } as const;

function isLang(value: string | null): value is LangCode {
  return value === "ja" || value === "ru" || value === "it" || value === "ar";
}

export function PlacementReadView() {
  const params = useSearchParams();
  const router = useRouter();
  const requested = params.get("language");
  const stored = useStoredLanguage();
  const language: LangCode = isLang(requested) ? requested : stored;
  const [read, setRead] = useState<PlacementRead | null>(null);
  const [picks, setPicks] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<PlacementResult | null>(null);

  useEffect(() => {
    let cancelled = false;
    setRead(null);
    setResult(null);
    setError(null);
    fetchPlacement(language)
      .then((data) => {
        if (cancelled) return;
        setRead(data);
        setPicks(data.questions.map(() => -1));
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not open the placement read.");
      });
    return () => {
      cancelled = true;
    };
  }, [language]);

  async function onSubmit() {
    if (!read || picks.some((pick) => pick < 0)) {
      setError("Answer each question.");
      return;
    }
    setSending(true);
    setError(null);
    try {
      const scored = await submitPlacement(language, picks);
      saveLanguage(language);
      setResult(scored);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save that level.");
    } finally {
      setSending(false);
    }
  }

  const font = readingFont(language);
  const name = NAMES[language];

  return (
    <div className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pb-24 pt-7 sm:px-8 sm:pt-9">
      <header className="flex items-center justify-between gap-4">
        <Link href="/library" className="t-quiet">
          ← Library
        </Link>
        <p className="t-eyebrow">{name}</p>
      </header>

      <Art
        key={language}
        src={`cliff-${language}`}
        className="cliff-fade -mb-10 ml-auto mt-4 hidden aspect-[4/3] w-[22rem] sm:block"
      />

      <h1 className="t-heading mt-10 text-[2rem] text-ink sm:mt-0 sm:text-[2.4rem]">
        {result ? `Your ${name} is at ${result.level}.` : "One short passage."}
      </h1>
      <p className="mt-3 max-w-[36rem] text-[15px] leading-relaxed text-ink/70">
        {result
          ? `${result.correct} of ${result.total}. The shelf will use this band.`
          : `Read it, then answer four questions. That sets your ${name} level.`}
      </p>

      {error ? <p className="mt-6 text-sm text-terracotta">{error}</p> : null}

      {read ? (
        <>
          <h2 dir={language === "ar" ? "rtl" : undefined} className={`mt-10 text-[1.8rem] leading-snug text-ink ${font}`}>
            {read.title}
          </h2>
          <PassageArticle
            tokens={read.tokens}
            language={language}
            selected={null}
            onSelect={() => undefined}
            className="mt-6"
          />
          {result ? (
            <button type="button" className="btn-primary mt-10 self-start" onClick={() => router.push("/library")}>
              Go to the shelf
            </button>
          ) : (
            <section className="mt-12 border-t border-rule pt-8">
              <ol className="flex flex-col gap-6">
                {read.questions.map((question, qIndex) => (
                  <li key={question.id}>
                    <p className="text-[15px] leading-relaxed text-ink">{question.prompt}</p>
                    <div className="mt-3 flex flex-col gap-2">
                      {question.choices.map((choice, cIndex) => (
                        <button
                          key={choice}
                          type="button"
                          onClick={() =>
                            setPicks((prev) => prev.map((value, index) => (index === qIndex ? cIndex : value)))
                          }
                          className={`rounded-card border px-3 py-2 text-left text-sm ${
                            picks[qIndex] === cIndex
                              ? "border-ink bg-paper-raised text-ink"
                              : "border-rule bg-paper text-ink hover:border-ink/30"
                          }`}
                        >
                          {choice}
                        </button>
                      ))}
                    </div>
                  </li>
                ))}
              </ol>
              <button
                type="button"
                disabled={sending || picks.some((pick) => pick < 0)}
                onClick={() => void onSubmit()}
                className="btn-primary mt-8 disabled:opacity-40"
              >
                {sending ? "Saving…" : "Set my level"}
              </button>
            </section>
          )}
        </>
      ) : !error ? (
        <p className="mt-10 text-sm text-ink/45">Opening the passage…</p>
      ) : null}
    </div>
  );
}
