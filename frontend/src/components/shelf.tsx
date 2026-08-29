"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { GenerateForm } from "@/components/generate-form";
import { fetchLibrary } from "@/lib/api";
import { loadLanguage, saveLanguage } from "@/lib/device";
import { LANGUAGES, type LangCode, type LibraryItem, type LibraryResponse } from "@/lib/types";

function lemmaLine(item: LibraryItem): string | null {
  const total = item.new_lemmas + item.recycled_lemmas;
  if (total === 0) return null;
  return `${item.new_lemmas} new · ${item.recycled_lemmas} known`;
}

function PassageCard({ item }: { item: LibraryItem }) {
  const ja = item.language === "ja";
  const lemmas = lemmaLine(item);
  return (
    <Link
      href={`/passage/${item.id}`}
      className={`block rounded-xl border px-4 py-3.5 transition hover:border-ink/30 ${
        item.recommended
          ? "border-ink bg-ink text-paper"
          : "border-rule bg-paper-raised text-ink"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className={`text-lg leading-snug ${ja ? "font-ja" : "font-reading"}`}>
          {item.title}
        </h3>
        <span
          className={`shrink-0 text-[11px] uppercase tracking-[0.14em] ${
            item.recommended ? "text-paper/60" : "text-ink/40"
          }`}
        >
          {item.level}
        </span>
      </div>
      <p className={`mt-1 text-sm ${item.recommended ? "text-paper/70" : "text-ink/50"}`}>
        {item.topic}
      </p>
      <p className={`mt-2 text-[13px] ${item.recommended ? "text-paper/55" : "text-ink/40"}`}>
        {item.word_count} words
        {lemmas ? ` · ${lemmas}` : ""}
        {item.read ? " · read" : ""}
      </p>
    </Link>
  );
}

export function Shelf() {
  const [language, setLanguage] = useState<LangCode>("ja");
  const [library, setLibrary] = useState<LibraryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [restockOpen, setRestockOpen] = useState(false);

  useEffect(() => {
    setLanguage(loadLanguage());
  }, []);

  const load = useCallback(async (lang: LangCode, signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLibrary(lang, signal);
      if (signal?.aborted) return;
      setLibrary(data);
    } catch (err) {
      if (signal?.aborted) return;
      setError(err instanceof Error ? err.message : "Could not load the shelf.");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const ac = new AbortController();
    void load(language, ac.signal);
    return () => ac.abort();
  }, [language, load]);

  function onLanguage(next: LangCode) {
    setLanguage(next);
    saveLanguage(next);
  }

  const nextItem = library?.items.find((item) => item.id === library.next_id) ?? null;
  const rest = (library?.items ?? []).filter((item) => item.id !== library?.next_id);

  return (
    <div className="flex flex-col gap-10">
      <div className="grid grid-cols-2 gap-2">
        {LANGUAGES.map((item) => {
          const active = item.id === language;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onLanguage(item.id)}
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

      {library ? (
        <p className="text-sm text-ink/55">
          Your {language === "ja" ? "Japanese" : "Russian"} level is{" "}
          <span className="font-medium text-ink">{library.placement}</span>
          {library.seen_lemmas > 0
            ? `. ${library.seen_lemmas} lemmas seen.`
            : ". Rate a passage to move it."}
        </p>
      ) : null}

      {error ? (
        <p className="rounded-lg border border-terracotta/30 bg-terracotta/10 px-4 py-3 text-sm text-terracotta">
          {error}
        </p>
      ) : null}

      {loading && !library ? (
        <p className="text-sm text-ink/45">Loading the shelf…</p>
      ) : null}

      {nextItem ? (
        <section className="flex flex-col gap-2">
          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
            Continue
          </p>
          <PassageCard item={nextItem} />
        </section>
      ) : null}

      {rest.length > 0 ? (
        <section className="flex flex-col gap-2">
          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-ink/50">
            The shelf
          </p>
          <div className="flex flex-col gap-2">
            {rest.map((item) => (
              <PassageCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      ) : null}

      <section>
        <button
          type="button"
          onClick={() => setRestockOpen((open) => !open)}
          className="text-[13px] tracking-wide text-ink/50 transition hover:text-ink"
        >
          {restockOpen ? "Hide restock" : "Restock the shelf"}
        </button>
        {restockOpen ? (
          <div className="mt-6">
            <GenerateForm language={language} restock />
          </div>
        ) : null}
      </section>
    </div>
  );
}
