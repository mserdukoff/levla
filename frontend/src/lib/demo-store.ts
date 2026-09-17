import { getDemoPassage, listDemoPassages } from "./demo-catalog";
import { isContentWord, type CefrLevel, type FeedbackRating, type LangCode, type LibraryItem, type LibraryResponse, type Passage, type PassageStats, type ReviewCard, type StarredWord, type Token } from "./types";

const KEY = "levla.demo.v1";
const LEVELS: CefrLevel[] = ["A1", "A2", "B1", "B2"];
const DEFAULT_LEVEL: CefrLevel = "A2";
const PLACEMENT_STREAK = 3;

type LangState = {
  placement: CefrLevel;
  consecutive_up: number;
  consecutive_down: number;
  seen: string[];
  read: string[];
};

type StarEntry = StarredWord & {
  reading: string | null;
  context: string | null;
  card_id: number;
};

type Store = {
  languages: Record<LangCode, LangState>;
  stars: StarEntry[];
  next_card_id: number;
};

function emptyLang(): LangState {
  return {
    placement: DEFAULT_LEVEL,
    consecutive_up: 0,
    consecutive_down: 0,
    seen: [],
    read: [],
  };
}

function empty(): Store {
  return {
    languages: {
      ja: emptyLang(),
      ru: emptyLang(),
      it: emptyLang(),
      ar: emptyLang(),
    },
    stars: [],
    next_card_id: 1,
  };
}

function load(): Store {
  if (typeof window === "undefined") return empty();
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return empty();
    const parsed = JSON.parse(raw) as Store;
    if (!parsed?.languages) return empty();
    return {
      ...empty(),
      ...parsed,
      languages: {
        ja: { ...emptyLang(), ...parsed.languages.ja },
        ru: { ...emptyLang(), ...parsed.languages.ru },
        it: { ...emptyLang(), ...parsed.languages.it },
        ar: { ...emptyLang(), ...parsed.languages.ar },
      },
      stars: parsed.stars ?? [],
      next_card_id: parsed.next_card_id ?? 1,
    };
  } catch {
    return empty();
  }
}

function save(store: Store): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, JSON.stringify(store));
}

function bumpLevel(level: CefrLevel, rating: FeedbackRating): CefrLevel {
  const idx = LEVELS.indexOf(level);
  if (rating === "too_easy") return LEVELS[Math.min(idx + 1, LEVELS.length - 1)];
  if (rating === "too_hard") return LEVELS[Math.max(idx - 1, 0)];
  return level;
}

function applyPlacement(lang: LangState, rating: FeedbackRating): CefrLevel {
  if (rating === "too_easy") {
    lang.consecutive_up += 1;
    lang.consecutive_down = 0;
    if (lang.consecutive_up >= PLACEMENT_STREAK) {
      lang.placement = bumpLevel(lang.placement, "too_easy");
      lang.consecutive_up = 0;
    }
  } else if (rating === "too_hard") {
    lang.consecutive_down += 1;
    lang.consecutive_up = 0;
    if (lang.consecutive_down >= PLACEMENT_STREAK) {
      lang.placement = bumpLevel(lang.placement, "too_hard");
      lang.consecutive_down = 0;
    }
  } else {
    lang.consecutive_up = 0;
    lang.consecutive_down = 0;
  }
  return lang.placement;
}

function uniqueContentLemmas(tokens: Token[], language: LangCode): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const tok of tokens) {
    if (!tok.lemma || !isContentWord(tok, language) || seen.has(tok.lemma)) continue;
    seen.add(tok.lemma);
    out.push(tok.lemma);
  }
  return out;
}

function lemmaTokenStats(tokens: Token[], language: LangCode, seen: Set<string>): { new_lemmas: number; recycled_lemmas: number } {
  let neu = 0;
  let recycled = 0;
  for (const tok of tokens) {
    if (!tok.lemma || !isContentWord(tok, language)) continue;
    if (seen.has(tok.lemma)) recycled += 1;
    else neu += 1;
  }
  return { new_lemmas: neu, recycled_lemmas: recycled };
}

function levelPriority(placement: CefrLevel): CefrLevel[] {
  const idx = LEVELS.indexOf(placement);
  const order: CefrLevel[] = [placement];
  if (idx + 1 < LEVELS.length) order.push(LEVELS[idx + 1]);
  if (idx - 1 >= 0) order.push(LEVELS[idx - 1]);
  for (const lv of LEVELS) {
    if (!order.includes(lv)) order.push(lv);
  }
  return order;
}

function pickNextId(language: LangCode, placement: CefrLevel, alreadyRead: Set<string>, excludeId?: string | null): string | null {
  const rows = listDemoPassages(language).filter((p) => p.calibration.passed);
  if (rows.length === 0) return null;
  for (const level of levelPriority(placement)) {
    const unread = rows.filter((p) => p.level === level && !alreadyRead.has(p.id) && p.id !== excludeId);
    if (unread.length > 0) {
      unread.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
      return unread[0].id;
    }
  }
  const rest = rows.filter((p) => p.id !== excludeId);
  if (rest.length === 0) return rows[0].id;
  rest.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
  return rest[0].id;
}

function contextSentence(passage: Passage, lemma: string): string | null {
  const hit = passage.tokens.findIndex((t) => t.lemma === lemma);
  if (hit < 0) return null;
  const ends = passage.language === "ja" ? /[。！？]/ : /[.!?…؟]/;
  let start = hit;
  while (start > 0 && !(!passage.tokens[start - 1].is_word && ends.test(passage.tokens[start - 1].text))) {
    start -= 1;
  }
  const bits: string[] = [];
  for (let i = start; i < passage.tokens.length; i++) {
    const tok = passage.tokens[i];
    bits.push(tok.text + (tok.ws ?? ""));
    if (!tok.is_word && ends.test(tok.text)) break;
  }
  const text = bits.join("").trim();
  return text || null;
}

export function demoLibrary(language: LangCode): LibraryResponse {
  const store = load();
  const lang = store.languages[language];
  const seen = new Set(lang.seen);
  const read = new Set(lang.read);
  const next_id = pickNextId(language, lang.placement, read);
  const items: LibraryItem[] = listDemoPassages(language).map((p) => {
    const stats = lemmaTokenStats(p.tokens, language, seen);
    const total = stats.new_lemmas + stats.recycled_lemmas;
    return {
      id: p.id,
      language: p.language,
      level: p.level,
      topic: p.topic,
      genre: p.genre,
      title: p.title,
      word_count: p.word_count,
      created_at: p.created_at,
      passed: p.calibration.passed,
      read: read.has(p.id),
      recommended: p.id === next_id,
      new_lemmas: stats.new_lemmas,
      recycled_lemmas: stats.recycled_lemmas,
      new_lemma_pct: total > 0 ? stats.new_lemmas / total : 0,
    };
  });
  items.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
  return {
    language,
    placement: lang.placement,
    next_id,
    seen_lemmas: lang.seen.length,
    items,
    words: store.stars
      .filter((s) => s.language === language)
      .map(({ lemma, gloss, passage_id, title, language: langCode }) => ({
        lemma,
        gloss,
        passage_id,
        title,
        language: langCode,
      })),
  };
}

export function demoPassageStats(id: string): PassageStats {
  const passage = getDemoPassage(id);
  if (!passage) {
    throw new Error("Passage not found.");
  }
  const store = load();
  const lang = store.languages[passage.language];
  const seen = new Set(lang.seen);
  const stats = lemmaTokenStats(passage.tokens, passage.language, seen);
  const read = new Set(lang.read);
  return {
    passage_id: id,
    language: passage.language,
    placement: lang.placement,
    read: read.has(id),
    new_lemmas: stats.new_lemmas,
    recycled_lemmas: stats.recycled_lemmas,
    next_id: pickNextId(passage.language, lang.placement, read, id),
    known_lemmas: lang.seen,
    starred_lemmas: store.stars.filter((s) => s.language === passage.language).map((s) => s.lemma),
  };
}

export function demoFeedback(passageId: string, rating: FeedbackRating) {
  const passage = getDemoPassage(passageId);
  if (!passage) {
    throw new Error("Passage not found.");
  }
  const store = load();
  const lang = store.languages[passage.language];
  const seen = new Set(lang.seen);
  const before = lemmaTokenStats(passage.tokens, passage.language, seen);
  const placement = applyPlacement(lang, rating);
  for (const lemma of uniqueContentLemmas(passage.tokens, passage.language)) {
    if (!seen.has(lemma)) {
      seen.add(lemma);
      lang.seen.push(lemma);
    }
  }
  if (!lang.read.includes(passageId)) lang.read.push(passageId);
  save(store);
  const read = new Set(lang.read);
  return {
    ok: true,
    passage_id: passageId,
    rating,
    placement,
    next_id: pickNextId(passage.language, placement, read, passageId),
    new_lemmas: before.new_lemmas,
    recycled_lemmas: before.recycled_lemmas,
  };
}

export function demoStarWord(body: {
  lemma: string;
  gloss?: string | null;
  passage_id?: string | null;
  language?: LangCode;
}): StarredWord {
  const store = load();
  const language = body.language ?? "ja";
  const passage = body.passage_id ? getDemoPassage(body.passage_id) : undefined;
  const existing = store.stars.find((s) => s.language === language && s.lemma === body.lemma);
  const reading = passage?.tokens.find((t) => t.lemma === body.lemma)?.morph?.reading ?? null;
  const context = passage ? contextSentence(passage, body.lemma) : null;
  if (existing) {
    if (body.gloss) existing.gloss = body.gloss;
    if (body.passage_id) {
      existing.passage_id = body.passage_id;
      existing.title = passage?.title ?? existing.title;
    }
    if (reading) existing.reading = reading;
    if (context) existing.context = context;
    save(store);
    return existing;
  }
  const entry: StarEntry = {
    lemma: body.lemma,
    gloss: body.gloss ?? null,
    passage_id: body.passage_id ?? null,
    title: passage?.title ?? null,
    language,
    reading,
    context,
    card_id: store.next_card_id++,
  };
  store.stars.unshift(entry);
  save(store);
  return entry;
}

export function demoUnstarWord(lemma: string, language: LangCode): void {
  const store = load();
  store.stars = store.stars.filter((s) => !(s.language === language && s.lemma === lemma));
  save(store);
}

export function demoReview(language: LangCode): { due: number; cards: ReviewCard[] } {
  const store = load();
  const cards: ReviewCard[] = store.stars
    .filter((s) => s.language === language)
    .map((s) => ({
      id: s.card_id,
      lemma: s.lemma,
      gloss: s.gloss,
      reading: s.reading,
      context: s.context,
      language: s.language,
      due_at: new Date().toISOString(),
    }));
  return { due: cards.length, cards };
}

export function demoSubmitReview(_cardId: number, _rating: "again" | "hard" | "good" | "easy") {
  return { ok: true };
}
