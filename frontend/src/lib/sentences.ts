import type { LangCode, Token } from "./types";

const JA_END = /[。！？]/;
const RU_END = /[.!?…]/;

export function tokenSentenceIndex(tokens: Token[], language: LangCode): number[] {
  const ids: number[] = [];
  let sid = 0;
  for (const tok of tokens) {
    ids.push(sid);
    const end = language === "ja" ? JA_END : RU_END;
    if (!tok.is_word && end.test(tok.text)) {
      sid += 1;
    }
  }
  return ids;
}

export function splitEnglishSentences(text: string): string[] {
  const trimmed = text.trim();
  if (!trimmed) return [];
  return trimmed
    .split(/(?<=[.!?])(?:\s+|$)/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function sentenceEnglish(
  tokens: Token[],
  language: LangCode,
  tokenIndex: number,
  translation: string | null,
): string | null {
  if (!translation || tokenIndex < 0 || tokenIndex >= tokens.length) return null;
  const ids = tokenSentenceIndex(tokens, language);
  const sid = ids[tokenIndex];
  const parts = splitEnglishSentences(translation);
  if (sid < parts.length) return parts[sid];
  return null;
}
