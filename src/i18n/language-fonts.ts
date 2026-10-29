import type { Language } from ".";

/** Share in-flight requests and keep successful stylesheets for later switches. */
export function createLanguageFontLoader(
  loaders: Record<Language, () => Promise<unknown>>,
) {
  const requests = new Map<Language, Promise<void>>();
  return (language: Language): Promise<void> => {
    let request = requests.get(language);
    if (!request) {
      request = loaders[language]().then(
        () => undefined,
        () => {
          // Retain system fallbacks offline; a later selection can retry.
          requests.delete(language);
        },
      );
      requests.set(language, request);
    }
    return request;
  };
}

// Keep separate import call sites: Vite extracts each CSS-only import as its own
// chunk, and can otherwise merge identical empty modules in a conditional return.
const fontImports = {
  ja: () => import("../styles/language-font-ja.css"),
  zh: () => import("../styles/language-font-zh.css"),
};
const failedStyles = new Set<Language>();

function importFontStyles(language: Language) {
  // A failed link may still have an opaque CSSStyleSheet. Track load failures
  // explicitly instead of using link.sheet as evidence that the CSS loaded.
  const failed = failedStyles.has(language)
    ? document.querySelector<HTMLLinkElement>(
        `link[rel="stylesheet"][href*="/language-font-${language}-"]`,
      )
    : null;
  const request = failed
    ? new Promise<void>((resolve, reject) => {
        const retry = failed.cloneNode() as HTMLLinkElement;
        retry.addEventListener("load", () => resolve(), { once: true });
        retry.addEventListener(
          "error",
          () => reject(new Error("Font stylesheet unavailable")),
          { once: true },
        );
        failed.replaceWith(retry);
      })
    : fontImports[language]();
  return request.then(
    () => {
      failedStyles.delete(language);
    },
    (error) => {
      failedStyles.add(language);
      throw error;
    },
  );
}

const loadFonts = createLanguageFontLoader({
  ja: () => importFontStyles("ja"),
  zh: () => importFontStyles("zh"),
});

export function loadLanguageFonts(language: Language): Promise<void> {
  // Language resolution is also used by Node tests without a stylesheet runtime.
  return typeof document === "undefined"
    ? Promise.resolve()
    : loadFonts(language);
}
