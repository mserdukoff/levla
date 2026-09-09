/**
 * Exam-seal inscriptions. One geometry in `seal.tsx`; adding a language is a
 * row here, not a new drawing. Missing keys fall back to Latin PASS / FAIL.
 *
 * Prefer the language’s short exam-stamp word (about 2–8 letters or 2–4 CJK).
 * If the native word is too long, keep the Latin fallback.
 */

export type SealScript = "cjk" | "cyrillic" | "latin";

export type SealCopy = {
  script: SealScript;
  pass: string;
  fail: string;
  rtl?: boolean;
};

export const SEAL_FALLBACK: SealCopy = {
  script: "latin",
  pass: "PASS",
  fail: "FAIL",
};

export const SEAL_COPY: Record<string, SealCopy> = {
  ja: { script: "cjk", pass: "合格", fail: "不合格" },
  ru: { script: "cyrillic", pass: "ЗАЧЁТ", fail: "НЕЗАЧЁТ" },
};

export function sealCopyFor(language: string): SealCopy {
  return SEAL_COPY[language] ?? SEAL_FALLBACK;
}

export function sealInscription(
  word: string,
  script: SealScript,
): { lines: string[]; fontSize: number } {
  const n = [...word].length;
  if (script === "cjk") {
    if (n <= 2) return { lines: [word], fontSize: 26 };
    if (n === 3) return { lines: [word], fontSize: 18 };
    return { lines: [word], fontSize: 14 };
  }
  if (n <= 4) return { lines: [word], fontSize: 17 };
  if (n === 5) return { lines: [word], fontSize: 13.5 };
  if (n <= 8) return { lines: [word], fontSize: Math.max(9, 68 / n) };
  const chars = [...word];
  const mid = Math.ceil(n / 2);
  return {
    lines: [chars.slice(0, mid).join(""), chars.slice(mid).join("")],
    fontSize: 11,
  };
}
