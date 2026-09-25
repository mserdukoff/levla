import { useSyncExternalStore } from "react";
import type { LangCode } from "./types";

const DEVICE_KEY = "lociros.device_id";
const LANG_KEY = "lociros.language";

export function getDeviceId(): string {
  if (typeof window === "undefined") return "ssr-device";
  let id = window.localStorage.getItem(DEVICE_KEY);
  if (!id || id.length < 8) {
    id = crypto.randomUUID();
    window.localStorage.setItem(DEVICE_KEY, id);
  }
  return id;
}

export function loadLanguage(): LangCode {
  if (typeof window === "undefined") return "ja";
  const value = window.localStorage.getItem(LANG_KEY);
  return value === "ru" || value === "ja" || value === "it" || value === "ar" ? value : "ja";
}

export function saveLanguage(language: LangCode): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LANG_KEY, language);
}

function subscribeStorage(onChange: () => void): () => void {
  window.addEventListener("storage", onChange);
  return () => window.removeEventListener("storage", onChange);
}

/** The saved language, rendered as "ja" during hydration so server and client markup match. */
export function useStoredLanguage(): LangCode {
  return useSyncExternalStore(subscribeStorage, loadLanguage, () => "ja");
}

const GRAMMAR_KEY = "lociros.grammar";

export function loadGrammarColors(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(GRAMMAR_KEY) === "1";
}

export function saveGrammarColors(on: boolean): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(GRAMMAR_KEY, on ? "1" : "0");
}

const FURIGANA_KEY = "lociros.furigana";

export function loadFurigana(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(FURIGANA_KEY) === "1";
}

export function saveFurigana(on: boolean): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(FURIGANA_KEY, on ? "1" : "0");
}

const FADE_KEY = "lociros.fade";

export function loadFadeKnown(): boolean {
  if (typeof window === "undefined") return true;
  const value = window.localStorage.getItem(FADE_KEY);
  if (value === null) return true;
  return value === "1";
}

export function saveFadeKnown(on: boolean): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(FADE_KEY, on ? "1" : "0");
}

export function deviceHeaders(json = false): HeadersInit {
  const headers: Record<string, string> = {
    "X-Device-Id": getDeviceId(),
  };
  if (json) headers["Content-Type"] = "application/json";
  return headers;
}
