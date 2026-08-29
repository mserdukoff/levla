"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { generatePassage } from "@/lib/api";
import { GENRES, LANGUAGES, LEVELS, type CefrLevel, type LangCode } from "@/lib/types";

export function GenerateForm({
  language: languageProp,
  restock = false,
}: {
  language?: LangCode;
  restock?: boolean;
}) {
  const router = useRouter();
  const [level, setLevel] = useState<CefrLevel>("A2");
  const [language, setLanguage] = useState<LangCode>(languageProp ?? "ja");
  const [topic, setTopic] = useState("");
  const [genre, setGenre] = useState<string | null>("daily_life");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (languageProp) setLanguage(languageProp);
  }, [languageProp]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = topic.trim();
    if (!trimmed) {
      setError("Give the passage a topic.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const passage = await generatePassage({
        level,
        topic: trimmed,
        genre,
        language,
      });
      router.push(`/passage/${passage.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-8">
      {!restock ? (
      <fieldset className="flex flex-col gap-3">
        <legend className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
          Language
        </legend>
        <div className="grid grid-cols-2 gap-2">
          {LANGUAGES.map((item) => {
            const active = item.id === language;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setLanguage(item.id)}
                className={`flex flex-col items-start rounded-lg border px-3 py-2.5 text-left transition ${
                  active
                    ? "border-ink bg-ink text-paper"
                    : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                }`}
              >
                <span className="text-sm font-medium">{item.label}</span>
                <span className={`mt-0.5 text-[13px] ${active ? "text-paper/70" : "text-ink/45"}`}>
                  {item.native}
                </span>
              </button>
            );
          })}
        </div>
      </fieldset>
      ) : null}

      <fieldset className="flex flex-col gap-3">
        <legend className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
          Level
        </legend>
        <div className="grid grid-cols-4 gap-2">
          {LEVELS.map((item) => {
            const active = item.id === level;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setLevel(item.id)}
                className={`flex flex-col items-start rounded-lg border px-3 py-2.5 text-left transition ${
                  active
                    ? "border-ink bg-ink text-paper"
                    : "border-rule bg-paper-raised text-ink hover:border-ink/30"
                }`}
              >
                <span className="font-display text-lg leading-none">{item.label}</span>
                <span
                  className={`mt-1 text-[11px] ${active ? "text-paper/70" : "text-ink/45"}`}
                >
                  {item.hint}
                </span>
              </button>
            );
          })}
        </div>
      </fieldset>

      <label className="flex flex-col gap-2">
        <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
          Topic
        </span>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder={
            language === "ja"
              ? "A morning at the market, a train to Kyoto…"
              : "A morning at the market, a train to Kazan…"
          }
          maxLength={200}
          className="rounded-lg border border-rule bg-paper-raised px-4 py-3 text-base text-ink outline-none placeholder:text-ink/30 focus:border-ink"
        />
      </label>

      <fieldset className="flex flex-col gap-3">
        <legend className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
          Genre
        </legend>
        <div className="flex flex-wrap gap-2">
          {GENRES.map((item) => {
            const active = item.id === genre;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setGenre(active ? null : item.id)}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                  active
                    ? "border-terracotta bg-terracotta text-paper"
                    : "border-rule bg-paper-raised text-ink/80 hover:border-ink/30"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </fieldset>

      {error ? (
        <p className="rounded-lg border border-terracotta/30 bg-terracotta/10 px-4 py-3 text-sm text-terracotta" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={loading}
        className="flex h-12 items-center justify-center rounded-lg bg-ink px-6 text-sm font-medium tracking-wide text-paper transition hover:bg-ink/90 disabled:cursor-wait disabled:opacity-70"
      >
        {loading ? "Writing and checking level…" : restock ? "Add to shelf" : "Generate passage"}
      </button>

      {loading ? (
        <p className="text-center text-sm text-ink/50">
          Constraining grammar to {level}, then validating every word. This
          usually takes 20–40 seconds.
        </p>
      ) : null}
    </form>
  );
}
