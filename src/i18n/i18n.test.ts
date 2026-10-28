import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { getLanguage, setLanguage, translate, LANGUAGE_KEY } from "./index";

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
