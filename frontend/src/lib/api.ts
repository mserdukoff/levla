import { deviceHeaders } from "./device";
import type {
  CefrLevel,
  FeedbackRating,
  FeedbackResult,
  LangCode,
  LibraryResponse,
  MeResponse,
  Passage,
  PassageStats,
  ReviewCard,
  StarredWord,
} from "./types";

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(" ");
    }
    return JSON.stringify(data);
  } catch {
    return res.statusText;
  }
}

function opts(init: RequestInit = {}, json = false): RequestInit {
  return {
    credentials: "include",
    ...init,
    headers: {
      ...deviceHeaders(json),
      ...(init.headers ?? {}),
    },
  };
}

export async function fetchMe(): Promise<MeResponse> {
  const res = await fetch("/api/me", opts({ cache: "no-store" }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function requestMagicLink(email: string): Promise<{ ok: boolean; link?: string }> {
  const res = await fetch("/api/auth/magic", opts({
    method: "POST",
    body: JSON.stringify({ email }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", opts({ method: "POST" }));
}

export async function generatePassage(body: {
  level: CefrLevel;
  topic: string;
  genre?: string | null;
  language: LangCode;
}): Promise<Passage> {
  const res = await fetch("/api/generate", opts({
    method: "POST",
    body: JSON.stringify({
      level: body.level,
      topic: body.topic,
      genre: body.genre || null,
      language: body.language,
    }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchLibrary(
  language: LangCode,
  signal?: AbortSignal,
): Promise<LibraryResponse> {
  const res = await fetch(`/api/library?language=${language}`, opts({
    cache: "no-store",
    signal,
  }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchPassage(id: string): Promise<Passage> {
  const res = await fetch(`/api/passages/${id}`, opts({ cache: "no-store" }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchTranslation(id: string): Promise<string> {
  const res = await fetch(`/api/passages/${id}/translation`, opts({ cache: "no-store" }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  const data: { translation: string } = await res.json();
  return data.translation;
}

export async function fetchPassageStats(id: string): Promise<PassageStats> {
  const res = await fetch(`/api/passages/${id}/stats`, opts({ cache: "no-store" }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function sendFeedback(
  passageId: string,
  rating: FeedbackRating,
): Promise<FeedbackResult> {
  const res = await fetch("/api/feedback", opts({
    method: "POST",
    body: JSON.stringify({ passage_id: passageId, rating }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function starWord(body: {
  lemma: string;
  gloss?: string | null;
  passage_id?: string | null;
  language?: LangCode;
}): Promise<StarredWord> {
  const res = await fetch("/api/words", opts({
    method: "POST",
    body: JSON.stringify(body),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function unstarWord(lemma: string, language: LangCode): Promise<void> {
  const res = await fetch("/api/words", opts({
    method: "DELETE",
    body: JSON.stringify({ lemma, language }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
}

export async function fetchReview(language: LangCode): Promise<{ due: number; cards: ReviewCard[] }> {
  const res = await fetch(`/api/review?language=${language}`, opts({ cache: "no-store" }));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function submitReview(cardId: number, rating: "again" | "hard" | "good" | "easy") {
  const res = await fetch("/api/review", opts({
    method: "POST",
    body: JSON.stringify({ card_id: cardId, rating }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function submitComprehension(passageId: string, answers: number[]) {
  const res = await fetch("/api/comprehension", opts({
    method: "POST",
    body: JSON.stringify({ passage_id: passageId, answers }),
  }, true));
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json() as Promise<{ ok: boolean; correct: number; total: number }>;
}

export async function recordEvent(kind: string, passageId?: string) {
  await fetch("/api/events", opts({
    method: "POST",
    body: JSON.stringify({ kind, passage_id: passageId ?? null }),
  }, true));
}
