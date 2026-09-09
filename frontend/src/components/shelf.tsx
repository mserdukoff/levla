"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { BandStrip } from "@/components/band";
import { GenerateForm } from "@/components/generate-form";
import { Segmented } from "@/components/segmented";
import { Seal } from "@/components/seal";
import { fetchLibrary, fetchMe, fetchReview, logout, requestMagicLink, unstarWord } from "@/lib/api";
import { getDeviceId, loadLanguage, saveLanguage } from "@/lib/device";
import {
  LANGUAGES,
  type LangCode,
  type LibraryItem,
  type LibraryResponse,
  type MeResponse,
  type StarredWord,
} from "@/lib/types";

const LANG_NAME: Record<LangCode, string> = { ja: "Japanese", ru: "Russian" };

function lemmaLine(item: LibraryItem): string | null {
  const total = item.new_lemmas + item.recycled_lemmas;
  if (total === 0) return null;
  return item.new_lemma_pct != null
    ? `${Math.round(item.new_lemma_pct * 100)}% new`
    : `${item.new_lemmas} new · ${item.recycled_lemmas} known`;
}

function metaLine(item: LibraryItem): string {
  const bits = [`${item.word_count} words`];
  const lemmas = lemmaLine(item);
  if (lemmas) bits.push(lemmas);
  if (item.has_audio) bits.push("audio");
  if (item.read) bits.push("read");
  return bits.join(" · ");
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="t-eyebrow">{children}</p>;
}

function WordsList({
  words,
  language,
  onRemove,
}: {
  words: StarredWord[];
  language: LangCode;
  onRemove: (lemma: string) => void;
}) {
  if (words.length === 0) return null;
  const font = language === "ja" ? "font-ja" : "font-reading";
  return (
    <section className="flex flex-col gap-3">
      <SectionLabel>Words</SectionLabel>
      <ul className="flex flex-col divide-y divide-rule border-y border-rule">
        {words.map((word) => (
          <li key={word.lemma} className="flex items-start justify-between gap-4 py-3">
            <div className="min-w-0">
              <p className="flex flex-wrap items-baseline gap-x-2.5">
                <span className={`text-[1.0625rem] text-ink ${font}`}>{word.lemma}</span>
                {word.gloss ? <span className="text-sm text-ink/55">{word.gloss}</span> : null}
              </p>
              {word.passage_id && word.title ? (
                <Link
                  href={`/passage/${word.passage_id}`}
                  className={`mt-0.5 block text-[13px] text-ink/40 transition-colors hover:text-ink ${font}`}
                >
                  {word.title}
                </Link>
              ) : null}
            </div>
            <button
              type="button"
              onClick={() => onRemove(word.lemma)}
              className="t-quiet shrink-0 underline decoration-ink/15 underline-offset-4"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
      <p className="t-quiet">
        Export{" "}
        <a
          href="/api/words/export.csv"
          className="underline decoration-ink/20 underline-offset-4 hover:text-ink"
        >
          CSV
        </a>
        {" · "}
        <a
          href="/api/words/export.apkg"
          className="underline decoration-ink/20 underline-offset-4 hover:text-ink"
        >
          Anki pack
        </a>
      </p>
    </section>
  );
}

/** The recommended passage: the one ink-on-paper inversion on the shelf. */
function ContinueCard({ item }: { item: LibraryItem }) {
  const font = item.language === "ja" ? "font-ja" : "font-reading";
  return (
    <Link
      href={`/passage/${item.id}`}
      className="group block rounded-card bg-ink px-6 py-6 text-paper transition-colors hover:bg-ink/90 sm:px-7 sm:py-7"
    >
      <div className="flex items-start justify-between gap-4">
        <p className="text-[13px] text-paper/60">{item.topic}</p>
        <div className="flex items-start gap-3">
          <Seal
            verdict={item.passed ? "pass" : "fail"}
            language={item.language}
            level={item.level}
            size="mark"
            inverted
          />
          <BandStrip level={item.level} inverted />
        </div>
      </div>
      <h3 className={`mt-5 text-[1.6rem] leading-[1.2] sm:text-[1.9rem] ${font}`}>{item.title}</h3>
      <div className="tnum mt-7 flex items-baseline justify-between gap-3 text-[13px]">
        <span className="text-paper/50">{metaLine(item)}</span>
        <span className="text-paper/80 transition-colors group-hover:text-paper">Read →</span>
      </div>
    </Link>
  );
}

/** Every other passage: a hairline row, not a card. */
function ShelfRow({ item }: { item: LibraryItem }) {
  const font = item.language === "ja" ? "font-ja" : "font-reading";
  return (
    <li>
      <Link
        href={`/passage/${item.id}`}
        className="group grid grid-cols-[1fr_auto] items-baseline gap-x-4 px-3 py-3.5 transition-colors hover:bg-paper-raised"
      >
        <h3 className={`text-[1.125rem] leading-snug text-ink ${font}`}>{item.title}</h3>
        <span className="tnum flex items-center gap-2 font-display text-[11px] tracking-[0.12em] text-ink/45">
          {!item.passed ? (
            <Seal
              verdict="fail"
              language={item.language}
              level={item.level}
              size="mark"
            />
          ) : null}
          {item.level}
          {item.chapter_index ? ` · ch ${item.chapter_index}` : ""}
        </span>
        <p className="tnum col-span-2 mt-1 text-[13px] text-ink/45">
          {item.topic} · {metaLine(item)}
        </p>
      </Link>
    </li>
  );
}

function AuthPanel({ me, onRefresh }: { me: MeResponse | null; onRefresh: () => void }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  if (!me) return null;
  if (me.authenticated) {
    return (
      <div className="flex items-baseline justify-between gap-3 border-y border-rule py-3 text-sm text-ink/60">
        <p>{me.display_name || me.email}</p>
        <button
          type="button"
          onClick={async () => {
            await logout();
            onRefresh();
          }}
          className="t-quiet underline decoration-ink/20 underline-offset-4"
        >
          Sign out
        </button>
      </div>
    );
  }
  const googleHref = `/api/auth/google?device_id=${encodeURIComponent(getDeviceId())}`;
  return (
    <form
      className="flex flex-col gap-3 border-y border-rule py-5"
      onSubmit={async (e) => {
        e.preventDefault();
        try {
          const data = await requestMagicLink(email);
          setMessage(
            data.link ? `Dev sign-in link: ${data.link}` : "Check your email for a sign-in link.",
          );
        } catch (err) {
          setMessage(err instanceof Error ? err.message : "Could not send link.");
        }
      }}
    >
      <p className="text-sm text-ink/55">
        Sign in to keep progress across devices and to restock custom texts.
      </p>
      <div className="flex items-end gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="field-line min-w-0 flex-1 text-sm!"
        />
        <button
          type="submit"
          className="h-9 shrink-0 rounded-card bg-ink px-3.5 text-sm text-paper transition-colors hover:bg-ink/90"
        >
          Email link
        </button>
      </div>
      <a href={googleHref} className="t-quiet underline decoration-ink/20 underline-offset-4">
        Continue with Google
      </a>
      {message ? <p className="break-all text-[13px] text-ink/55">{message}</p> : null}
    </form>
  );
}

export function Shelf() {
  const [language, setLanguage] = useState<LangCode>("ja");
  const [library, setLibrary] = useState<LibraryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [restockOpen, setRestockOpen] = useState(false);
  const [me, setMe] = useState<MeResponse | null>(null);
  const [due, setDue] = useState(0);
  const showRussian = me?.show_russian === true;

  useEffect(() => {
    const saved = loadLanguage();
    if (saved === "ja") setLanguage("ja");
  }, []);

  useEffect(() => {
    if (showRussian) {
      if (loadLanguage() === "ru") setLanguage("ru");
      return;
    }
    if (language === "ru") {
      setLanguage("ja");
      saveLanguage("ja");
    }
  }, [showRussian, language]);

  const refreshMe = useCallback(() => {
    void fetchMe()
      .then(setMe)
      .catch(() => setMe(null));
  }, []);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  const load = useCallback(
    async (lang: LangCode, signal?: AbortSignal) => {
      const requested = !showRussian && lang === "ru" ? "ja" : lang;
      setLoading(true);
      setError(null);
      try {
        const data = await fetchLibrary(requested, signal);
        if (signal?.aborted) return;
        setLibrary(data);
      } catch (err) {
        if (signal?.aborted) return;
        setError(err instanceof Error ? err.message : "Could not load the shelf.");
      } finally {
        if (!signal?.aborted) setLoading(false);
      }
    },
    [showRussian],
  );

  useEffect(() => {
    const ac = new AbortController();
    void load(language, ac.signal);
    void fetchReview(language)
      .then((data) => setDue(data.due))
      .catch(() => setDue(0));
    return () => ac.abort();
  }, [language, load]);

  function onLanguage(next: LangCode) {
    setLanguage(next);
    saveLanguage(next);
  }

  async function onRemoveWord(lemma: string) {
    try {
      await unstarWord(lemma, language);
      setLibrary((prev) =>
        prev ? { ...prev, words: (prev.words ?? []).filter((w) => w.lemma !== lemma) } : prev,
      );
    } catch {
      /* keep the list */
    }
  }

  const nextItem = library?.items.find((item) => item.id === library.next_id) ?? null;
  const rest = (library?.items ?? []).filter((item) => item.id !== library?.next_id);
  const langs = showRussian ? LANGUAGES : LANGUAGES.filter((l) => l.id === "ja");
  const langName = LANG_NAME[language];

  function openRestock() {
    setRestockOpen(true);
    document.getElementById("restock")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const restockForm =
    me?.require_auth && !me.authenticated ? (
      <p className="text-sm text-ink/55">
        Sign in to generate a custom-topic passage. The catalog below is free to read.
      </p>
    ) : (
      <GenerateForm language={language} restock remaining={me?.generate_remaining} />
    );

  return (
    <div className="flex flex-col gap-12">
      <header className="flex items-center justify-between gap-4">
        <Link
          href="/"
          className="font-display text-[1.375rem] font-medium tracking-[-0.02em] text-ink"
        >
          Levla
        </Link>
        {langs.length > 1 ? (
          <Segmented
            ariaLabel="Language"
            size="sm"
            options={langs.map((l) => ({ id: l.id, label: l.label, hint: l.native }))}
            value={language}
            onChange={onLanguage}
          />
        ) : null}
      </header>

      <section>
        <p className="t-kicker">{langName} · Library</p>
        {library ? (
          <>
            <h1 className="t-heading mt-4 text-[2rem] text-ink sm:text-[2.5rem]">
              Your {langName} is at {library.placement}.
            </h1>
            <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3">
              <BandStrip level={library.placement} />
              <p className="tnum text-[13px] text-ink/50">
                {library.seen_lemmas > 0
                  ? `${library.seen_lemmas} lemmas seen.`
                  : "Rate a passage to move it."}{" "}
                Three ratings in a row move the band.
              </p>
            </div>
          </>
        ) : (
          <h1 className="t-heading mt-4 text-[2rem] text-ink/40 sm:text-[2.5rem]">
            {loading ? "Opening the shelf…" : `Your ${langName} shelf.`}
          </h1>
        )}
      </section>

      {me?.require_auth ? <AuthPanel me={me} onRefresh={refreshMe} /> : null}

      {error ? (
        <p className="rounded-card border border-terracotta/30 bg-terracotta/10 px-4 py-3 text-sm text-terracotta">
          {error}
        </p>
      ) : null}

      {nextItem ? (
        <section className="flex flex-col gap-3">
          <SectionLabel>Continue</SectionLabel>
          <ContinueCard item={nextItem} />
        </section>
      ) : null}

      {due > 0 ? (
        <Link
          href="/review"
          className="group flex items-baseline justify-between gap-4 border-y border-rule py-3.5 transition-colors hover:bg-paper-raised"
        >
          <span className="tnum text-[1.0625rem] text-ink">{due} saved words due for review</span>
          <span className="t-quiet group-hover:text-ink">Review →</span>
        </Link>
      ) : null}

      {library?.words && library.words.length > 0 ? (
        <WordsList words={library.words} language={language} onRemove={onRemoveWord} />
      ) : null}

      {rest.length > 0 ? (
        <section className="flex flex-col gap-3">
          <SectionLabel>The shelf</SectionLabel>
          <ul className="-mx-3 flex flex-col divide-y divide-rule border-y border-rule">
            {rest.map((item) => (
              <ShelfRow key={item.id} item={item} />
            ))}
          </ul>
        </section>
      ) : null}

      <section id="restock" className="scroll-mt-8 flex flex-col gap-3">
        <SectionLabel>Restock</SectionLabel>
        {restockOpen ? (
          <>
            <p className="max-w-[26rem] text-[15px] leading-relaxed text-ink/60">
              A new {langName} passage, written to a band and checked before it lands on the
              shelf.
            </p>
            <div className="mt-4">{restockForm}</div>
            <button
              type="button"
              onClick={() => setRestockOpen(false)}
              className="t-quiet mt-2 self-start"
            >
              Hide restock
            </button>
          </>
        ) : (
          <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
            <button type="button" onClick={openRestock} className="t-quiet text-ink">
              Restock the shelf →
            </button>
            {due === 0 ? (
              <Link href="/review" className="t-quiet">
                Review saved words
              </Link>
            ) : null}
          </div>
        )}
      </section>
    </div>
  );
}
