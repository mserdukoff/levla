export type CefrLevel = "A1" | "A2" | "B1" | "B2";
export type LangCode = "ru" | "ja";
export type FeedbackRating = "too_easy" | "too_hard" | "just_right";

export type MorphInfo = {
  lemma: string;
  pos: string | null;
  case: string | null;
  gender: string | null;
  number: string | null;
  tense: string | null;
  aspect: string | null;
  mood: string | null;
  reading: string | null;
  form: string | null;
  pos_detail?: string | null;
  conj_type?: string | null;
};

export type ConjPiece = {
  text: string;
  label: string;
};

export type KanjiPart = {
  char: string;
  reading: string | null;
  on: string[];
  kun: string[];
  meaning: string;
  strokes?: number | null;
  jlpt?: number | null;
  grade?: number | null;
  freq?: number | null;
  radical?: string | null;
  radical_name?: string | null;
  parts?: string[];
  nanori?: string[];
};

export type Token = {
  text: string;
  ws: string;
  is_word: boolean;
  lemma: string | null;
  morph: MorphInfo | null;
  gloss: string | null;
  level: string | null;
  kanji?: KanjiPart[];
  role?: string | null;
  conj?: ConjPiece[];
  conj_id?: number | null;
};

export type Calibration = {
  passed: boolean;
  attempts: number;
  overlevel_lemma_rate: number;
  subordinate_rate: number;
  forbidden_case_rate: number;
  forbidden_tense_rate: number;
  forbidden_pos_rate: number;
  flags: string[];
  warnings: string[];
  allowed_constructions?: string[];
  forbidden_used?: string[];
  banned_constructions?: string[];
  sample_lemmas?: string[];
};

export type AudioCue = {
  index: number;
  start_ms: number;
  end_ms: number;
  text: string;
};

export type ComprehensionQuestion = {
  id: string;
  prompt: string;
  choices: string[];
  answer_index: number;
};

export type Passage = {
  id: string;
  language: LangCode;
  level: CefrLevel;
  topic: string;
  genre: string | null;
  title: string;
  text: string;
  tokens: Token[];
  calibration: Calibration;
  word_count: number;
  created_at: string;
  translation?: string | null;
  audio_url?: string | null;
  audio_cues?: AudioCue[];
  series_id?: string | null;
  chapter_index?: number | null;
  comprehension?: ComprehensionQuestion[];
  shelf_status?: string;
};

export type LibraryItem = {
  id: string;
  language: LangCode;
  level: CefrLevel;
  topic: string;
  genre: string | null;
  title: string;
  word_count: number;
  created_at: string;
  passed: boolean;
  read: boolean;
  recommended: boolean;
  new_lemmas: number;
  recycled_lemmas: number;
  series_id?: string | null;
  chapter_index?: number | null;
  has_audio?: boolean;
  new_lemma_pct?: number;
};

export type LibraryResponse = {
  language: LangCode;
  placement: CefrLevel;
  next_id: string | null;
  seen_lemmas: number;
  items: LibraryItem[];
  words?: StarredWord[];
};

export type StarredWord = {
  lemma: string;
  gloss: string | null;
  passage_id: string | null;
  title: string | null;
  language: LangCode;
};

export type PassageStats = {
  passage_id: string;
  language: LangCode;
  placement: CefrLevel;
  read: boolean;
  new_lemmas: number;
  recycled_lemmas: number;
  next_id: string | null;
  known_lemmas?: string[];
  starred_lemmas?: string[];
};

export type FeedbackResult = {
  ok: boolean;
  passage_id: string;
  rating: FeedbackRating;
  placement: CefrLevel | null;
  next_id: string | null;
  new_lemmas: number;
  recycled_lemmas: number;
};

export type GenerateJobStatus = "pending" | "running" | "completed" | "failed";

export type GenerateJobResponse = {
  job_id: string;
  status: GenerateJobStatus;
  passage: Passage | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
};

export type MeResponse = {
  authenticated: boolean;
  user_id: number | null;
  email: string | null;
  display_name: string | null;
  guest: boolean;
  show_russian: boolean;
  generate_remaining: number | null;
  require_auth: boolean;
};

export type ReviewCard = {
  id: number;
  lemma: string;
  gloss: string | null;
  reading: string | null;
  context: string | null;
  language: LangCode;
  due_at: string;
};

export const LANGUAGES: { id: LangCode; label: string; native: string }[] = [
  { id: "ru", label: "Russian", native: "Русский" },
  { id: "ja", label: "Japanese", native: "日本語" },
];

export const LEVELS: { id: CefrLevel; label: string; hint: string }[] = [
  { id: "A1", label: "A1", hint: "Beginner" },
  { id: "A2", label: "A2", hint: "Elementary" },
  { id: "B1", label: "B1", hint: "Intermediate" },
  { id: "B2", label: "B2", hint: "Upper-int." },
];

export const GENRES: { id: string; label: string }[] = [
  { id: "daily_life", label: "Daily life" },
  { id: "travel", label: "Travel" },
  { id: "news", label: "News" },
  { id: "folklore", label: "Folklore" },
  { id: "work", label: "Work" },
];

export function morphLine(morph: MorphInfo): string {
  const parts = [
    morph.aspect,
    morph.tense,
    morph.mood === "impr" ? "imperative" : null,
    morph.case,
    morph.gender,
    morph.number,
    morph.pos && !morph.case ? morph.pos : null,
  ].filter(Boolean);
  return parts.join(" · ");
}

export function jaGrammarLine(token: Token): string {
  switch (token.role) {
    case "topic":
      return "topic marker";
    case "subject":
      return "subject marker";
    case "object":
      return "object marker";
    case "particle": {
      const detail = token.morph?.pos_detail;
      if (detail === "case") return "case particle";
      if (detail === "binding") return "binding particle";
      if (detail === "conjunctive") return "conjunctive particle";
      if (detail === "final") return "sentence particle";
      if (detail === "adverbial") return "adverbial particle";
      return "particle";
    }
    case "verb":
      return "verb";
    case "aux":
      return "auxiliary";
    case "adj":
      if (token.morph?.pos === "i-adj") return "i-adjective";
      if (token.morph?.pos === "na-adj") return "na-adjective";
      return "adjective";
    case "adverb":
      return "adverb";
    default:
      return "";
  }
}

const JA_CONTENT = new Set(["noun", "verb", "i-adj", "na-adj", "adverb"]);
const RU_CONTENT = new Set([
  "NOUN",
  "ADJF",
  "ADJS",
  "VERB",
  "INFN",
  "ADVB",
  "PRED",
  "NUMR",
]);

export function isContentWord(token: Token, language: LangCode): boolean {
  const pos = token.morph?.pos;
  if (!pos) return false;
  return language === "ja" ? JA_CONTENT.has(pos) : RU_CONTENT.has(pos);
}

const KANJI = /[\u4e00-\u9faf]/;

export function kanjiChars(text: string): string[] {
  return [...text].filter((ch) => KANJI.test(ch));
}

export function furiganaReading(token: Token): string | null {
  const reading = token.morph?.reading;
  if (!reading || !KANJI.test(token.text)) return null;
  return reading;
}
