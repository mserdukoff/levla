import { deviceHeaders } from "./device";
import type {
  CefrLevel,
  FeedbackRating,
  FeedbackResult,
  LangCode,
  LibraryResponse,
  Passage,
  PassageStats,
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

export async function generatePassage(body: {
  level: CefrLevel;
  topic: string;
  genre?: string | null;
  language: LangCode;
}): Promise<Passage> {
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: deviceHeaders(true),
    body: JSON.stringify({
      level: body.level,
      topic: body.topic,
      genre: body.genre || null,
      language: body.language,
    }),
  });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchLibrary(
  language: LangCode,
  signal?: AbortSignal,
): Promise<LibraryResponse> {
  const res = await fetch(`/api/library?language=${language}`, {
    cache: "no-store",
    headers: deviceHeaders(),
    signal,
  });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchPassage(id: string): Promise<Passage> {
  const res = await fetch(`/api/passages/${id}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function fetchTranslation(id: string): Promise<string> {
  const res = await fetch(`/api/passages/${id}/translation`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  const data: { translation: string } = await res.json();
  return data.translation;
}

export async function fetchPassageStats(id: string): Promise<PassageStats> {
  const res = await fetch(`/api/passages/${id}/stats`, {
    cache: "no-store",
    headers: deviceHeaders(),
  });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}

export async function sendFeedback(
  passageId: string,
  rating: FeedbackRating,
): Promise<FeedbackResult> {
  const res = await fetch("/api/feedback", {
    method: "POST",
    headers: deviceHeaders(true),
    body: JSON.stringify({ passage_id: passageId, rating }),
  });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json();
}
