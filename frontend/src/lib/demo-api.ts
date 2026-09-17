import { getDemoPassage } from "./demo-catalog";
import {
  demoFeedback,
  demoLibrary,
  demoPassageStats,
  demoReview,
  demoStarWord,
  demoSubmitReview,
  demoUnstarWord,
} from "./demo-store";
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

export async function fetchMe(): Promise<MeResponse> {
  return {
    authenticated: false,
    user_id: null,
    email: null,
    display_name: null,
    guest: true,
    show_russian: true,
    show_italian: true,
    show_arabic: true,
    generate_remaining: null,
    require_auth: false,
  };
}

export async function requestMagicLink(_email: string): Promise<{ ok: boolean; link?: string }> {
  return { ok: false };
}

export async function logout(): Promise<void> {}

export async function generatePassage(_body: {
  level: CefrLevel;
  topic: string;
  genre?: string | null;
  language: LangCode;
}): Promise<Passage> {
  throw new Error("This static demo does not generate new passages. Open a title from the shelf.");
}

export async function fetchLibrary(language: LangCode, _signal?: AbortSignal): Promise<LibraryResponse> {
  return demoLibrary(language);
}

export async function fetchPassage(id: string): Promise<Passage> {
  const passage = getDemoPassage(id);
  if (!passage) throw new Error("Passage not found.");
  return passage;
}

export async function fetchTranslation(id: string): Promise<string> {
  const passage = getDemoPassage(id);
  if (!passage?.translation) throw new Error("No English for this passage yet.");
  return passage.translation;
}

export async function fetchPassageStats(id: string): Promise<PassageStats> {
  return demoPassageStats(id);
}

export async function sendFeedback(passageId: string, rating: FeedbackRating): Promise<FeedbackResult> {
  return demoFeedback(passageId, rating);
}

export async function starWord(body: {
  lemma: string;
  gloss?: string | null;
  passage_id?: string | null;
  language?: LangCode;
}): Promise<StarredWord> {
  return demoStarWord(body);
}

export async function unstarWord(lemma: string, language: LangCode): Promise<void> {
  demoUnstarWord(lemma, language);
}

export async function fetchReview(language: LangCode): Promise<{ due: number; cards: ReviewCard[] }> {
  return demoReview(language);
}

export async function submitReview(cardId: number, rating: "again" | "hard" | "good" | "easy") {
  return demoSubmitReview(cardId, rating);
}

export async function submitComprehension(_passageId: string, _answers: number[]) {
  return { ok: true, correct: 0, total: 0 };
}

export async function recordEvent(_kind: string, _passageId?: string) {}
