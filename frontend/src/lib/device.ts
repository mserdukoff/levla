const DEVICE_KEY = "levla.device_id";
const LANG_KEY = "levla.language";

export function getDeviceId(): string {
  if (typeof window === "undefined") return "ssr-device";
  let id = window.localStorage.getItem(DEVICE_KEY);
  if (!id || id.length < 8) {
    id = crypto.randomUUID();
    window.localStorage.setItem(DEVICE_KEY, id);
  }
  return id;
}

export function loadLanguage(): "ru" | "ja" {
  if (typeof window === "undefined") return "ja";
  const value = window.localStorage.getItem(LANG_KEY);
  return value === "ru" || value === "ja" ? value : "ja";
}

export function saveLanguage(language: "ru" | "ja"): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LANG_KEY, language);
}

export function deviceHeaders(json = false): HeadersInit {
  const headers: Record<string, string> = {
    "X-Device-Id": getDeviceId(),
  };
  if (json) headers["Content-Type"] = "application/json";
  return headers;
}
