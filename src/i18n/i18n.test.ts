import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { afterEach, test } from "node:test";
import { runInNewContext } from "node:vm";
import {
  getLanguage,
  resolveLanguage,
  setLanguage,
  translate,
  LANGUAGE_KEY,
} from "./index";

const languageCases = [
  { saved: null, locale: "zh-CN", expected: "zh" },
  { saved: null, locale: "zh-Hant-TW", expected: "zh" },
  { saved: null, locale: "zh-HK", expected: "zh" },
  { saved: null, locale: "ja-JP", expected: "ja" },
  { saved: null, locale: "en-US", expected: "ja" },
  { saved: null, locale: "fr-FR", expected: "ja" },
  { saved: null, locale: undefined, expected: "ja" },
  { saved: "zh", locale: "ja-JP", expected: "zh" },
  { saved: "ja", locale: "zh-CN", expected: "ja" },
  { saved: "en", locale: "zh-CN", expected: "zh" },
  { saved: "", locale: "en-US", expected: "ja" },
] as const;

test("initial language follows the primary browser locale with Japanese fallback", () => {
  for (const { saved, locale, expected } of languageCases) {
    assert.equal(
      resolveLanguage(saved, locale),
      expected,
      `${saved}/${locale}`,
    );
  }
});

test("first-paint language agrees with the application before modules load", () => {
  const html = readFileSync(
    new URL("../../index.html", import.meta.url),
    "utf8",
  );
  const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script);
  for (const { saved, locale, expected } of languageCases) {
    for (const blocked of [false, true]) {
      const root = { lang: "ja", setAttribute() {} };
      runInNewContext(script, {
        document: { documentElement: root },
        navigator: {
          languages: locale ? [locale, "zh-CN"] : [],
          language: locale,
        },
        localStorage: {
          getItem(key: string) {
            if (blocked) throw new Error("storage blocked");
            return key === LANGUAGE_KEY ? saved : null;
          },
        },
      });
      const target = blocked ? resolveLanguage(null, locale) : expected;
      assert.equal(root.lang, target === "zh" ? "zh-CN" : "ja");
    }
  }
});

const storage = new Map<string, string>();
Object.defineProperty(globalThis, "localStorage", {
  configurable: true,
  value: {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => storage.set(key, value),
  },
});
afterEach(() => {
  setLanguage("zh");
  storage.clear();
});

test("language selection persists separately from learning progress", () => {
  storage.set("word-atlas:v2:word-atlas-open", "existing-progress");
  setLanguage("ja");
  assert.equal(getLanguage(), "ja");
  assert.equal(translate("收藏", "お気に入り"), "お気に入り");
  assert.equal(storage.get(LANGUAGE_KEY), "ja");
  assert.equal(
    storage.get("word-atlas:v2:word-atlas-open"),
    "existing-progress",
  );
  setLanguage("zh");
  assert.equal(translate("收藏", "お気に入り"), "收藏");
});

test("blocked storage does not prevent language changes", () => {
  const original = localStorage.setItem;
  localStorage.setItem = () => {
    throw new Error("storage blocked");
  };
  try {
    setLanguage("ja");
    assert.equal(getLanguage(), "ja");
    assert.equal(translate("练习", "練習"), "練習");
  } finally {
    localStorage.setItem = original;
  }
});

test("explicitly selecting the current language saves the preference", () => {
  const current = getLanguage();
  storage.delete(LANGUAGE_KEY);
  setLanguage(current);
  assert.equal(storage.get(LANGUAGE_KEY), current);
});
