import assert from "node:assert/strict";
import { test } from "node:test";
import { createLanguageFontLoader } from "./language-fonts";

test("language fonts load only on demand and share in-flight and completed requests", async () => {
  const calls = { ja: 0, zh: 0 };
  let finish!: () => void;
  const load = createLanguageFontLoader({
    ja: () => {
      calls.ja++;
      return new Promise<void>((resolve) => {
        finish = resolve;
      });
    },
    zh: async () => {
      calls.zh++;
    },
  });
  assert.deepEqual(calls, { ja: 0, zh: 0 });
  const first = load("ja");
  assert.equal(load("ja"), first);
  assert.deepEqual(calls, { ja: 1, zh: 0 });
  finish();
  await first;
  assert.equal(load("ja"), first);
  await load("zh");
  assert.deepEqual(calls, { ja: 1, zh: 1 });
});

test("failed font requests keep the app usable and can be retried", async () => {
  let calls = 0;
  const load = createLanguageFontLoader({
    ja: async () => {
      if (++calls === 1) throw new Error("offline");
    },
    zh: async () => undefined,
  });
  await assert.doesNotReject(load("ja"));
  await load("ja");
  await load("ja");
  assert.equal(calls, 2);
});
