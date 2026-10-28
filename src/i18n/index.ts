import { useSyncExternalStore } from "react";

export type Language = "zh" | "ja";
export const LANGUAGE_KEY = "word-atlas:language";

function readLanguage(): Language {
  try {
    return localStorage.getItem(LANGUAGE_KEY) === "ja" ? "ja" : "zh";
  } catch {
    return "zh";
  }
}

let language = readLanguage();
const listeners = new Set<() => void>();
const translators = {
  zh: (zh: string, _ja: string) => zh,
  ja: (_zh: string, ja: string) => ja,
};

export const getLanguage = () => language;
export const translate = (zh: string, ja: string) =>
  translators[language](zh, ja);

export function setLanguage(next: Language) {
  if (next === language) return;
  language = next;
  try {
    localStorage.setItem(LANGUAGE_KEY, next);
  } catch {
    // The selection still works for this visit when browser storage is unavailable.
  }
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", (event) => {
    if (event.key !== LANGUAGE_KEY && event.key !== null) return;
    const next = readLanguage();
    if (next === language) return;
    language = next;
    listeners.forEach((listener) => listener());
  });
}

export function useI18n() {
  const language = useSyncExternalStore(
    subscribe,
    getLanguage,
    () => "zh" as const,
  );
  return { language, t: translators[language] };
}
