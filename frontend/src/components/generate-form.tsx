"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { GenerationProgress } from "@/components/generation-progress";
import { Segmented } from "@/components/segmented";
import { generatePassage } from "@/lib/api";
import { GENRES, LANGUAGES, LEVELS, type CefrLevel, type LangCode } from "@/lib/types";

export function GenerateForm({
  language: languageProp,
  restock = false,
  remaining = null,
}: {
  language?: LangCode;
  restock?: boolean;
  remaining?: number | null;
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
    <form onSubmit={onSubmit} className="flex flex-col gap-9">
      {!restock ? (
        <fieldset className="flex flex-col gap-3">
          <legend className="t-eyebrow mb-3">Language</legend>
          <Segmented
            ariaLabel="Language"
            options={LANGUAGES.map((l) => ({ id: l.id, label: l.label, hint: l.native }))}
            value={language}
            onChange={setLanguage}
          />
        </fieldset>
      ) : null}

      <fieldset className="flex flex-col gap-3">
        <legend className="t-eyebrow mb-3">Level</legend>
        <Segmented
          ariaLabel="CEFR level"
          options={LEVELS.map((l) => ({ id: l.id, label: l.label, hint: l.hint }))}
          value={level}
          onChange={setLevel}
        />
      </fieldset>

      <label className="flex flex-col gap-3">
        <span className="t-eyebrow">Topic</span>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder={
            language === "ja"
              ? "A morning at the market, a train to Kyoto…"
              : "A morning at the market, a train to Kazan…"
          }
          maxLength={200}
          className="field-line"
        />
      </label>

      <fieldset className="flex flex-col gap-3">
        <legend className="t-eyebrow mb-3">Genre</legend>
        <div className="flex flex-wrap gap-2">
          {GENRES.map((item) => {
            const active = item.id === genre;
            return (
              <button
                key={item.id}
                type="button"
                aria-pressed={active}
                onClick={() => setGenre(active ? null : item.id)}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors ${
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
        <p
          className="rounded-card border border-terracotta/30 bg-terracotta/10 px-4 py-3 text-sm text-terracotta"
          role="alert"
        >
          {error}
        </p>
      ) : null}

      <div className="flex flex-col gap-3">
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Writing and checking level…" : restock ? "Add to shelf" : "Generate passage"}
        </button>
        {remaining != null && !loading ? (
          <p className="tnum text-center text-[13px] text-ink/45">
            {remaining} custom passages left this month.
          </p>
        ) : null}
      </div>

      {loading ? (
        <div className="border-t border-rule pt-6">
          <GenerationProgress level={level} language={language} />
        </div>
      ) : null}
    </form>
  );
}
