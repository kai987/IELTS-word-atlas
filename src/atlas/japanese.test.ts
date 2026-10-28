import assert from "node:assert/strict";
import { test } from "node:test";
import { applyJapaneseEntry } from "./japanese";
import type { Entry } from "./types";

const source: Entry = {
  id: "library",
  w: "library",
  uk: "/ˈlaɪbrəri/",
  us: "/ˈlaɪbreri/",
  senses: [{ pos: "n.", zh: "图书馆", en: "A place to borrow books." }],
  ex: [{ en: "I borrowed books from the library.", zh: "我从图书馆借了书。" }],
  col: ["library card｜借书证"],
  fam: ["librarian (n.)"],
  syn: [],
  ant: [],
  tip: "可数名词。",
  cefr: "A1",
  topic: "education",
  m: 31,
};
const ja = {
  id: "library",
  senses: ["図書館"],
  ex: ["図書館で本を借りました。"],
  col: ["library card｜図書館の利用カード"],
  tip: "可算名詞。",
  note: "",
};

test("Japanese overlay keeps identity, English, pronunciation and media intact", () => {
  const localized = applyJapaneseEntry(source, ja);
  assert.equal(localized.senses[0].zh, "図書館");
  assert.equal(localized.ex[0].zh, "図書館で本を借りました。");
  assert.equal(localized.w, source.w);
  assert.equal(localized.id, source.id);
  assert.equal(localized.m, source.m);
  assert.equal(localized.uk, source.uk);
  assert.equal(localized.ex[0].en, source.ex[0].en);
  assert.equal(localized.senses[0].en, source.senses[0].en);
  assert.equal(source.senses[0].zh, "图书馆");
});

test("misaligned or missing translations fail explicitly", () => {
  assert.throws(
    () => applyJapaneseEntry(source, { ...ja, id: "other" }),
    /library/,
  );
  assert.throws(
    () => applyJapaneseEntry(source, { ...ja, senses: [] }),
    /library/,
  );
  assert.throws(() => applyJapaneseEntry(source, { ...ja, ex: [] }), /library/);
  assert.throws(
    () => applyJapaneseEntry(source, { ...ja, col: [] }),
    /library/,
  );
});
