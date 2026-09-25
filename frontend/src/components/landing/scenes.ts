import type { LangCode } from "@/lib/types";

type Stratum = { top: string; level: string; label: string };

type Scene = {
  /** Share of the cliff image width where the rock face begins; labels sit left of it. */
  face: string;
  /** Vertical centre of each carved band in /art/cliff-{lang}, as a share of the image height. */
  strata: Stratum[];
  lede: string;
  vistaCaption: string;
  explore: string;
};

const LEVELS = ["Everyday words", "Daily life", "Stories", "Culture and history"];

function strata(tops: string[]): Stratum[] {
  return tops.map((top, i) => ({ top, level: ["A1", "A2", "B1", "B2"][i], label: LEVELS[i] }));
}

export const SCENES: Record<LangCode, Scene> = {
  ja: {
    face: "37%",
    strata: strata(["26%", "39%", "51.5%", "70%"]),
    lede: "Graded readers in Japanese, from the first greeting to stories and the classics underneath. Tap any word for the reading, the grammar, and every kanji inside it.",
    vistaCaption: "Kyoto, from a temple veranda.",
    explore:
      "Passages are set in stations, bakeries, temples, and offices, so each word arrives with the place it belongs to. Politeness arrives in order: です and ます first, keigo much later.",
  },
  ar: {
    face: "39%",
    strata: strata(["29%", "44%", "58%", "74%"]),
    lede: "Graded readers in Arabic, from everyday phrases to the roots and patterns that hold the language together. Tap any word for the root, the vowels, and the grammar.",
    vistaCaption: "An old city, from under the arcade.",
    explore:
      "Passages are set in markets, kitchens, streets, and classrooms, in Modern Standard Arabic. Each word shows its root, so one new verb opens a family of words you already half know.",
  },
  it: {
    face: "37%",
    strata: strata(["27%", "38.5%", "50%", "64%"]),
    lede: "Graded readers in Italian, from ciao at the café to the Latin under every word. Tap any word for the meaning, the tense, and the form.",
    vistaCaption: "Florence, from a loggia above the city.",
    explore:
      "Passages are set in piazzas, trains, kitchens, and shops. The tenses arrive in the order learners need them, so the passato prossimo is there long before the subjunctive.",
  },
  ru: {
    face: "39%",
    strata: strata(["29%", "40%", "53.5%", "66.5%"]),
    lede: "Graded readers in Russian, from привет to the cases, aspects, and stories that give it depth. Tap any word for the case, the aspect, and the mood.",
    vistaCaption: "Saint Petersburg, across the Neva.",
    explore:
      "Passages are set in flats, courtyards, trams, and dachas. Cases arrive one at a time, so the instrumental waits until the others feel ordinary.",
  },
};
