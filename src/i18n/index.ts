import { useSyncExternalStore } from "react";
import { loadLanguageFonts } from "./language-fonts";

export type Language = "zh" | "ja";
export const LANGUAGE_KEY = "word-atlas:language";

export function resolveLanguage(
  savedLanguage: string | null,
  browserLanguage?: string,
): Language {
  if (savedLanguage === "zh" || savedLanguage === "ja") return savedLanguage;
  return /^zh(?:[-_]|$)/i.test(browserLanguage ?? "") ? "zh" : "ja";
}

function readLanguage(): Language {
  let savedLanguage: string | null = null;
  try {
    savedLanguage = localStorage.getItem(LANGUAGE_KEY);
  } catch {
    // Browser language still works when browser storage is unavailable.
  }
  const browserLanguage =
    typeof navigator === "undefined"
      ? undefined
      : navigator.languages?.[0] || navigator.language;
  return resolveLanguage(savedLanguage, browserLanguage);
}

let language = readLanguage();
let languageRequest = 0;
const listeners = new Set<() => void>();
const translators = {
  zh: (zh: string, _ja: string) => zh,
  ja: (_zh: string, ja: string) => ja,
};

export const getLanguage = () => language;
export const translate = (zh: string, ja: string) =>
  translators[language](zh, ja);

async function applyLanguage(next: Language) {
  const request = ++languageRequest;
  await loadLanguageFonts(next);
  // A later selection (or storage event) wins, even if its CSS loaded first.
  if (request !== languageRequest || next === language) return;
  language = next;
  listeners.forEach((listener) => listener());
}

export function setLanguage(next: Language): Promise<void> {
  try {
    localStorage.setItem(LANGUAGE_KEY, next);
  } catch {
    // The selection still works for this visit when browser storage is unavailable.
  }
  return applyLanguage(next);
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
    void applyLanguage(next);
  });
}

export function useI18n() {
  const language = useSyncExternalStore(
    subscribe,
    getLanguage,
    () => "ja" as const,
  );
  return { language, t: translators[language] };
}
