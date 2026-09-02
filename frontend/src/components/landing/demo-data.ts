import type { CefrLevel, ConjPiece, KanjiPart, LangCode, MorphInfo, Token } from "@/lib/types";

/*
  Hand-authored sample passages for the landing page, in the same Token shape
  the API returns, so the hero renders through the real reader components.
  Morph values follow the backend's mapping (case nom/gen/dat/acc/ins/prep,
  tense pres/past/fut, number sg/pl, aspect impf/perf; Japanese POS labels
  noun/verb/i-adj/na-adj/particle/aux/adverb/pronoun).
*/

const EMPTY_MORPH: MorphInfo = {
  lemma: "",
  pos: null,
  case: null,
  gender: null,
  number: null,
  tense: null,
  aspect: null,
  mood: null,
  reading: null,
  form: null,
};

const KANJI: Record<string, Omit<KanjiPart, "reading">> = {
  朝: { char: "朝", on: ["チョウ"], kun: ["あさ"], meaning: "morning; dynasty; regime", strokes: 12, jlpt: 4, grade: 2, freq: 244, radical: "月", radical_name: "moon", parts: ["十", "日", "月"], nanori: ["あした", "あす"] },
  駅: { char: "駅", on: ["エキ"], kun: [], meaning: "station", strokes: 14, jlpt: 4, grade: 3, freq: 724, radical: "馬", radical_name: "horse", parts: ["馬", "尺"], nanori: [] },
  近: { char: "近", on: ["キン", "コン"], kun: ["ちか.い"], meaning: "near; early; akin; tantamount", strokes: 7, jlpt: 4, grade: 2, freq: 194, radical: "辶", radical_name: "walk", parts: ["斤", "辶"], nanori: ["おう", "ちか"] },
  屋: { char: "屋", on: ["オク"], kun: ["や"], meaning: "roof; house; shop; dealer; seller", strokes: 9, jlpt: 4, grade: 3, freq: 662, radical: "尸", radical_name: "corpse", parts: ["尸", "至"], nanori: [] },
  行: { char: "行", on: ["コウ", "ギョウ", "アン"], kun: ["い.く", "ゆ.く", "おこな.う"], meaning: "going; journey; carry out; line", strokes: 6, jlpt: 5, grade: 2, freq: 20, radical: "行", radical_name: "go", parts: ["行"], nanori: ["いき", "なみ"] },
  店: { char: "店", on: ["テン"], kun: ["みせ", "たな"], meaning: "store; shop", strokes: 8, jlpt: 4, grade: 2, freq: 585, radical: "广", radical_name: "dotted cliff", parts: ["广", "占"], nanori: [] },
  人: { char: "人", on: ["ジン", "ニン"], kun: ["ひと", "-り", "-と"], meaning: "person", strokes: 2, jlpt: 5, grade: 1, freq: 5, radical: "人", radical_name: "man", parts: ["人"], nanori: ["じ", "と", "ね"] },
  元: { char: "元", on: ["ゲン", "ガン"], kun: ["もと"], meaning: "beginning; former time; origin", strokes: 4, jlpt: 4, grade: 2, freq: 192, radical: "儿", radical_name: "legs", parts: ["二", "儿"], nanori: ["ちか", "はじめ"] },
  気: { char: "気", on: ["キ", "ケ"], kun: ["いき"], meaning: "spirit; mind; air; atmosphere; mood", strokes: 6, jlpt: 5, grade: 1, freq: 113, radical: "气", radical_name: "steam", parts: ["气", "メ"], nanori: [] },
  買: { char: "買", on: ["バイ"], kun: ["か.う"], meaning: "buy", strokes: 12, jlpt: 5, grade: 2, freq: 520, radical: "貝", radical_name: "shell", parts: ["罒", "貝"], nanori: [] },
  公: { char: "公", on: ["コウ", "ク"], kun: ["おおやけ"], meaning: "public; prince; official; governmental", strokes: 4, jlpt: 4, grade: 2, freq: 99, radical: "八", radical_name: "eight", parts: ["八", "厶"], nanori: ["いさお", "きみ", "たか"] },
  園: { char: "園", on: ["エン"], kun: ["その"], meaning: "park; garden; yard; farm", strokes: 13, jlpt: 3, grade: 2, freq: 1015, radical: "囗", radical_name: "enclosure", parts: ["囗", "土", "口", "衣"], nanori: ["おん"] },
  食: { char: "食", on: ["ショク", "ジキ"], kun: ["く.う", "く.らう", "た.べる", "は.む"], meaning: "eat; food", strokes: 9, jlpt: 5, grade: 2, freq: 328, radical: "食", radical_name: "eat", parts: ["人", "良"], nanori: ["ぐい"] },
  天: { char: "天", on: ["テン"], kun: ["あまつ", "あめ", "あま-"], meaning: "heavens; sky; imperial", strokes: 4, jlpt: 4, grade: 1, freq: 512, radical: "大", radical_name: "big", parts: ["一", "大"], nanori: ["あき", "たか"] },
  持: { char: "持", on: ["ジ"], kun: ["も.つ", "-も.ち", "も.てる"], meaning: "hold; have", strokes: 9, jlpt: 4, grade: 3, freq: 76, radical: "扌", radical_name: "hand", parts: ["土", "寸", "扌"], nanori: ["もち"] },
};

function kanji(spec: [string, string | null][]): KanjiPart[] {
  return spec.map(([char, reading]) => ({ ...KANJI[char], reading }));
}

function punct(text: string, ws = ""): Token {
  return { text, ws, is_word: false, lemma: null, morph: null, gloss: null, level: null };
}

type JaSpec = {
  lemma?: string;
  pos: string;
  reading?: string;
  level?: CefrLevel | null;
  gloss?: string;
  role?: string;
  detail?: string;
  form?: string;
  conj?: ConjPiece[];
  cid?: number;
  kanji?: [string, string | null][];
};

function ja(text: string, s: JaSpec): Token {
  const lemma = s.lemma ?? text;
  return {
    text,
    ws: "",
    is_word: true,
    lemma,
    morph: {
      ...EMPTY_MORPH,
      lemma,
      pos: s.pos,
      reading: s.reading ?? null,
      pos_detail: s.detail ?? null,
      form: s.form ?? null,
    },
    gloss: s.gloss ?? null,
    level: s.level === undefined ? "A1" : s.level,
    role: s.role ?? null,
    conj: s.conj,
    conj_id: s.cid ?? null,
    kanji: s.kanji ? kanji(s.kanji) : undefined,
  };
}

type RuSpec = {
  lemma?: string;
  pos: string;
  case?: string;
  gender?: string;
  number?: string;
  tense?: string;
  aspect?: string;
  level?: CefrLevel | null;
  gloss?: string;
  role?: string;
  ws?: string;
};

function ru(text: string, s: RuSpec): Token {
  const lemma = s.lemma ?? text.toLowerCase();
  return {
    text,
    ws: s.ws ?? " ",
    is_word: true,
    lemma,
    morph: {
      ...EMPTY_MORPH,
      lemma,
      pos: s.pos,
      case: s.case ?? null,
      gender: s.gender ?? null,
      number: s.number ?? null,
      tense: s.tense ?? null,
      aspect: s.aspect ?? null,
    },
    gloss: s.gloss ?? null,
    level: s.level === undefined ? "A1" : s.level,
    role: s.role ?? null,
  };
}

const POLITE_PAST = (stem: string): ConjPiece[] => [
  { text: stem, label: "stem" },
  { text: "まし", label: "polite" },
  { text: "た", label: "past" },
];

export type DemoPassage = {
  language: LangCode;
  level: CefrLevel;
  topic: string;
  genre: string;
  title: string;
  tokens: Token[];
  /** token index preselected on first paint */
  initial: number;
};

const JA_TOKENS: Token[] = [
  ja("朝", { pos: "noun", reading: "あさ", gloss: "morning", kanji: [["朝", "あさ"]] }),
  punct("、"),
  ja("駅", { pos: "noun", reading: "えき", gloss: "station", kanji: [["駅", "えき"]] }),
  ja("の", { pos: "particle", role: "particle", detail: "case", gloss: "of; ’s" }),
  ja("近く", { pos: "noun", reading: "ちかく", level: "A2", gloss: "near; the vicinity", kanji: [["近", "ちか"]] }),
  ja("の", { pos: "particle", role: "particle", detail: "case", gloss: "of; ’s" }),
  ja("パン屋", { pos: "noun", reading: "ぱんや", level: "A2", gloss: "bakery", kanji: [["屋", "や"]] }),
  ja("に", { pos: "particle", role: "particle", detail: "case", gloss: "to; at" }),
  ja("行き", { lemma: "行く", pos: "verb", reading: "いき", gloss: "to go", role: "verb", cid: 1, conj: POLITE_PAST("行き"), kanji: [["行", "い"]] }),
  ja("まし", { lemma: "ます", pos: "aux", role: "aux", gloss: "polite marker", cid: 1, conj: POLITE_PAST("行き") }),
  ja("た", { pos: "aux", role: "aux", gloss: "past tense", cid: 1, conj: POLITE_PAST("行き") }),
  punct("。"),
  ja("店", { pos: "noun", reading: "みせ", gloss: "shop; store", kanji: [["店", "みせ"]] }),
  ja("の", { pos: "particle", role: "particle", detail: "case", gloss: "of; ’s" }),
  ja("人", { pos: "noun", reading: "ひと", gloss: "person", kanji: [["人", "ひと"]] }),
  ja("は", { pos: "particle", role: "topic", detail: "binding", gloss: "topic marker" }),
  ja("いつも", { pos: "adverb", role: "adverb", gloss: "always" }),
  ja("元気", { pos: "na-adj", reading: "げんき", role: "adj", gloss: "cheerful; healthy", cid: 2, conj: [{ text: "元気", label: "stem" }, { text: "です", label: "copula" }], kanji: [["元", "げん"], ["気", "き"]] }),
  ja("です", { pos: "aux", role: "aux", gloss: "is (polite)", cid: 2, conj: [{ text: "元気", label: "stem" }, { text: "です", label: "copula" }] }),
  punct("。"),
  ja("私", { pos: "pronoun", reading: "わたし", gloss: "I; me" }),
  ja("は", { pos: "particle", role: "topic", detail: "binding", gloss: "topic marker" }),
  ja("メロンパン", { pos: "noun", level: "A2", gloss: "melon bread" }),
  ja("と", { pos: "particle", role: "particle", detail: "case", gloss: "and; with" }),
  ja("コーヒー", { pos: "noun", gloss: "coffee" }),
  ja("を", { pos: "particle", role: "object", detail: "case", gloss: "object marker" }),
  ja("買い", { lemma: "買う", pos: "verb", reading: "かい", gloss: "to buy", role: "verb", cid: 3, conj: POLITE_PAST("買い"), kanji: [["買", "か"]] }),
  ja("まし", { lemma: "ます", pos: "aux", role: "aux", gloss: "polite marker", cid: 3, conj: POLITE_PAST("買い") }),
  ja("た", { pos: "aux", role: "aux", gloss: "past tense", cid: 3, conj: POLITE_PAST("買い") }),
  punct("。"),
  ja("公園", { pos: "noun", reading: "こうえん", gloss: "park", kanji: [["公", "こう"], ["園", "えん"]] }),
  ja("で", { pos: "particle", role: "particle", detail: "case", gloss: "at; in (place of action)" }),
  ja("パン", { pos: "noun", gloss: "bread" }),
  ja("を", { pos: "particle", role: "object", detail: "case", gloss: "object marker" }),
  ja("食べ", { lemma: "食べる", pos: "verb", reading: "たべ", gloss: "to eat", role: "verb", cid: 4, conj: POLITE_PAST("食べ"), kanji: [["食", "た"]] }),
  ja("まし", { lemma: "ます", pos: "aux", role: "aux", gloss: "polite marker", cid: 4, conj: POLITE_PAST("食べ") }),
  ja("た", { pos: "aux", role: "aux", gloss: "past tense", cid: 4, conj: POLITE_PAST("食べ") }),
  punct("。"),
  ja("天気", { pos: "noun", reading: "てんき", gloss: "weather", kanji: [["天", "てん"], ["気", "き"]] }),
  ja("が", { pos: "particle", role: "subject", detail: "case", gloss: "subject marker" }),
  ja("よく", { lemma: "良い", pos: "i-adj", role: "adj", gloss: "good", cid: 5, conj: [{ text: "よく", label: "stem" }, { text: "て", label: "te-form" }] }),
  ja("て", { pos: "particle", role: "aux", detail: "conjunctive", gloss: "and (linking)", cid: 5, conj: [{ text: "よく", label: "stem" }, { text: "て", label: "te-form" }] }),
  punct("、"),
  ja("気持ち", { pos: "noun", reading: "きもち", level: "A2", gloss: "feeling; mood", kanji: [["気", "き"], ["持", "も"]] }),
  ja("が", { pos: "particle", role: "subject", detail: "case", gloss: "subject marker" }),
  ja("よかっ", { lemma: "良い", pos: "i-adj", role: "adj", gloss: "good", cid: 6, conj: [{ text: "よかっ", label: "stem" }, { text: "た", label: "past" }, { text: "です", label: "copula" }] }),
  ja("た", { pos: "aux", role: "aux", gloss: "past tense", cid: 6, conj: [{ text: "よかっ", label: "stem" }, { text: "た", label: "past" }, { text: "です", label: "copula" }] }),
  ja("です", { pos: "aux", role: "aux", gloss: "is (polite)", cid: 6, conj: [{ text: "よかっ", label: "stem" }, { text: "た", label: "past" }, { text: "です", label: "copula" }] }),
  punct("。"),
];

const RU_TOKENS: Token[] = [
  ru("Каждое", { lemma: "каждый", pos: "ADJF", case: "acc", gender: "neut", number: "sg", gloss: "each; every", role: "adj" }),
  ru("утро", { pos: "NOUN", case: "acc", gender: "neut", number: "sg", gloss: "morning" }),
  ru("я", { pos: "NPRO", case: "nom", number: "sg", gloss: "I" }),
  ru("иду", { lemma: "идти", pos: "VERB", aspect: "impf", tense: "pres", number: "sg", gloss: "to go (on foot)", role: "verb" }),
  ru("на", { pos: "PREP", gloss: "on; to", role: "particle" }),
  ru("рынок", { pos: "NOUN", case: "acc", gender: "masc", number: "sg", level: "A2", gloss: "market", ws: "" }),
  punct(".", " "),
  ru("Там", { pos: "ADVB", gloss: "there", role: "adverb" }),
  ru("продают", { lemma: "продавать", pos: "VERB", aspect: "impf", tense: "pres", number: "pl", level: "A2", gloss: "to sell", role: "verb" }),
  ru("свежий", { pos: "ADJF", case: "acc", gender: "masc", number: "sg", level: "A2", gloss: "fresh", role: "adj" }),
  ru("хлеб", { pos: "NOUN", case: "acc", gender: "masc", number: "sg", gloss: "bread" }),
  ru("и", { pos: "CONJ", gloss: "and", role: "particle" }),
  ru("сыр", { pos: "NOUN", case: "acc", gender: "masc", number: "sg", gloss: "cheese", ws: "" }),
  punct(".", " "),
  ru("Я", { lemma: "я", pos: "NPRO", case: "nom", number: "sg", gloss: "I" }),
  ru("покупаю", { lemma: "покупать", pos: "VERB", aspect: "impf", tense: "pres", number: "sg", gloss: "to buy", role: "verb" }),
  ru("яблоки", { lemma: "яблоко", pos: "NOUN", case: "acc", gender: "neut", number: "pl", gloss: "apple" }),
  ru("и", { pos: "CONJ", gloss: "and", role: "particle" }),
  ru("говорю", { lemma: "говорить", pos: "VERB", aspect: "impf", tense: "pres", number: "sg", gloss: "to say; to speak", role: "verb" }),
  ru("продавцу", { lemma: "продавец", pos: "NOUN", case: "dat", gender: "masc", number: "sg", level: "A2", gloss: "seller; shop assistant", ws: "" }),
  punct(":", " "),
  punct("«"),
  ru("Доброе", { lemma: "добрый", pos: "ADJF", case: "nom", gender: "neut", number: "sg", gloss: "kind; good", role: "adj" }),
  ru("утро", { pos: "NOUN", case: "nom", gender: "neut", number: "sg", gloss: "morning", ws: "" }),
  punct("!"),
  punct("»", " "),
  ru("Потом", { pos: "ADVB", gloss: "then; afterwards", role: "adverb" }),
  ru("я", { pos: "NPRO", case: "nom", number: "sg", gloss: "I" }),
  ru("иду", { lemma: "идти", pos: "VERB", aspect: "impf", tense: "pres", number: "sg", gloss: "to go (on foot)", role: "verb" }),
  ru("домой", { pos: "ADVB", gloss: "home (direction)", role: "adverb" }),
  ru("и", { pos: "CONJ", gloss: "and", role: "particle" }),
  ru("пью", { lemma: "пить", pos: "VERB", aspect: "impf", tense: "pres", number: "sg", gloss: "to drink", role: "verb" }),
  ru("чай", { pos: "NOUN", case: "acc", gender: "masc", number: "sg", gloss: "tea", ws: "" }),
  punct("."),
];

export const DEMO: Record<LangCode, DemoPassage> = {
  ja: {
    language: "ja",
    level: "A2",
    topic: "A bakery near the station",
    genre: "Daily life",
    title: "朝のパン屋",
    tokens: JA_TOKENS,
    initial: JA_TOKENS.findIndex((t) => t.text === "食べ"),
  },
  ru: {
    language: "ru",
    level: "A2",
    topic: "A morning at the market",
    genre: "Daily life",
    title: "Утро на рынке",
    tokens: RU_TOKENS,
    initial: RU_TOKENS.findIndex((t) => t.text === "продавцу"),
  },
};

/* ---------- prompted-vs-checked comparison ---------- */

export type DriftSegment = { text: string; flag?: string };

export type DriftSample = {
  prompt: string;
  drifted: DriftSegment[];
  driftedSummary: string;
  checked: string;
  checkedReport: { k: string; v: string }[];
  checkedSummary: string;
};

export const DRIFT: Record<LangCode, DriftSample> = {
  ja: {
    prompt: "“Write something easy for a beginner learning Japanese.”",
    drifted: [
      { text: "駅前のパン屋で" },
      { text: "働いている", flag: "too advanced" },
      { text: "田中さんは", flag: "too advanced" },
      { text: "、毎朝五時に起きます。焼きたてのパンを買いに来るお客様が" },
      { text: "いらっしゃる", flag: "too advanced" },
      { text: "と、「おはようございます」と言います。もし雨が" },
      { text: "降ったら", flag: "too advanced" },
      { text: "、お客様は少なくなります。" },
    ],
    driftedSummary: "Too advanced in 4 places, five sentences in",
    checked:
      "田中さんは駅の前のパン屋で働きます。毎朝五時に起きて、パンを焼きます。八時に店を開けます。お客さんはパンを買って、「おはようございます」と言います。雨の日はお客さんが少ないです。",
    checkedReport: [
      { k: "New words", v: "3%, all within reach" },
      { k: "Grammar kept out", v: "nothing beyond simple past and present tense" },
      { k: "What slipped through", v: "nothing" },
    ],
    checkedSummary: "Reads exactly like it says it does",
  },
  ru: {
    prompt: "“Write something easy for a beginner learning Russian.”",
    drifted: [
      { text: "Каждое утро Анна, " },
      { text: "живущая", flag: "too advanced" },
      { text: " рядом с рынком, покупает свежий хлеб. " },
      { text: "Возвращаясь", flag: "too advanced" },
      { text: " домой, она разговаривает с соседом, " },
      { text: "который", flag: "too advanced" },
      { text: " работает " },
      { text: "пекарем", flag: "too advanced" },
      { text: ". Если " },
      { text: "бы", flag: "too advanced" },
      { text: " у неё было больше времени, она бы пекла хлеб сама." },
    ],
    driftedSummary: "Too advanced in 5 places, one sentence in",
    checked:
      "Каждое утро Анна идёт на рынок. Там она покупает свежий хлеб и сыр. Потом она идёт домой и говорит соседу: «Доброе утро!». Сосед работает в пекарне. Анна любит хлеб из пекарни, но у неё мало времени.",
    checkedReport: [
      { k: "New words", v: "4%, all within reach" },
      { k: "Grammar kept out", v: "no cases or verb forms you haven't met yet" },
      { k: "What slipped through", v: "nothing" },
    ],
    checkedSummary: "Reads exactly like it says it does",
  },
};
