import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import { after, before, test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { chromium } from "playwright";
import { auditTypography, typographyReportErrors } from "../scripts/typography-audit.mjs";

// Exercise the built CSS chunks, including their GitHub Pages subpath.
let browser;
let server;
let baseURL;
let serverOutput = "";
const contexts = new Set();

before(async () => {
  const html = await readFile(new URL("../dist/index.html", import.meta.url), "utf8");
  const entry = html.match(/<script\b[^>]*\bsrc="([^"]*\/assets\/[^"]+)"/);
  assert.ok(entry, "Build the production site before running test:typography");
  const entryPath = new URL(entry[1], "http://localhost").pathname;
  const base = entryPath.slice(0, entryPath.lastIndexOf("/assets/") + 1);
  const port = process.env.TYPOGRAPHY_PORT || "5193";
  baseURL = `http://127.0.0.1:${port}${base}`;
  server = spawn(process.execPath, [
    "node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1",
    "--port", port, "--strictPort", "--base", base,
  ], { cwd: new URL("..", import.meta.url), stdio: ["ignore", "pipe", "pipe"] });
  for (const stream of [server.stdout, server.stderr]) {
    stream.on("data", (data) => { serverOutput = (serverOutput + data).slice(-6000); });
  }
  let ready = false;
  for (let attempt = 0; attempt < 100 && server.exitCode === null; attempt++) {
    try { ready = (await fetch(baseURL)).ok; } catch { /* preview is starting */ }
    if (ready) break;
    await delay(100);
  }
  assert.ok(ready, `Production preview did not start:\n${serverOutput}`);
  browser = await chromium.launch();
}, { timeout: 25_000 });

after(async () => {
  await Promise.all([...contexts].map((context) => context.close()));
  await browser?.close();
  server?.kill("SIGTERM");
});

async function newPage({ width = 1280, locale = "ja-JP" } = {}) {
  const context = await browser.newContext({
    viewport: { width, height: width < 600 ? 844 : 900 },
    locale,
    reducedMotion: "reduce",
    serviceWorkers: "block",
  });
  contexts.add(context);
  // Only settings are seeded; locale resolution still uses the browser preference.
  await context.addInitScript(() => {
    localStorage.setItem("word-atlas:settings", JSON.stringify({
      onboarded: true, splash: false, ambience: "off", autoplay: false,
      sfx: false, theme: "dark",
    }));
    localStorage.setItem("word-atlas:guide:atlas-view:v1", "1");
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  return { page, errors };
}

async function ready(page) {
  await page.locator("main .display").first().waitFor({ state: "visible" });
  await page.evaluate(() => document.fonts.ready);
}

async function audit(page, label) {
  const faces = await page.evaluate(async () => {
    const fonts = await document.fonts.load('400 15px "Noto Sans JP Variable"', "日本語");
    return fonts.map((font) => ({ family: font.family, status: font.status }));
  });
  assert.ok(faces.length > 0, `${label}: the Japanese stylesheet must register real font faces`);
  assert.ok(
    faces.every((font) => font.family.includes("Noto Sans JP Variable") && font.status === "loaded"),
    `${label}: the Japanese UI font must actually load`,
  );
  const report = await page.evaluate(auditTypography);
  assert.deepEqual(typographyReportErrors(report), [], label);
  return report;
}

async function fontOf(locator) {
  return locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return { family: style.fontFamily, size: +style.fontSize.slice(0, -2), weight: style.fontWeight };
  });
}

async function loadedFontLanguages(page) {
  return page.evaluate(() => [...document.styleSheets]
    .map((sheet) => {
      const language = sheet.href?.match(/\/language-font-(ja|zh)-[^/]+\.css(?:\?|$)/)?.[1];
      if (!language) return;
      // Chromium can retain an opaque CSSStyleSheet after a failed request.
      try { return sheet.cssRules.length > 0 ? language : undefined; }
      catch { return undefined; }
    })
    .filter(Boolean));
}

for (const width of [1280, 390]) {
  test(`Japanese font roles and the inclusive 15px boundary at ${width}px`, { timeout: 120_000 }, async (t) => {
    const { page, errors } = await newPage({ width });
    for (const route of ["", "atlas?view=grid&level=A2", "atlas?view=list&level=A2", "practice", "me", "about"]) {
      await page.goto(`${baseURL}#/${route}`);
      await ready(page);
      const report = await audit(page, route || "today");
      t.diagnostic(`${route || "today"}: ${report.smallJapanese.length} small Japanese elements checked`);
      const heading = await fontOf(page.locator("main .display").first());
      assert.ok(heading.size > 15 && heading.family.includes("Mincho"), `${route}: large Japanese heading keeps the reading face`);
      const navigation = await fontOf(page.locator(".topnav a:visible, .tabbar a:visible").first());
      assert.ok(navigation.family.includes("Noto Sans JP Variable"));
      assert.equal(navigation.weight, "500");
      if (route === "practice") {
        const action = await fontOf(page.getByRole("button", { name: "練習を始める", exact: true }));
        assert.ok(action.family.includes("Noto Sans JP Variable"));
        assert.equal(action.weight, "600");
      }
    }
    await page.goto(`${baseURL}#/atlas?view=grid`);
    await ready(page);
    await page.locator(".tile").first().click();
    await page.locator(".entry .ex-zh").first().waitFor({ state: "visible" });
    await page.evaluate(() => document.fonts.ready);
    await audit(page, "entry detail");
    const meaning = await fontOf(page.locator(".entry .senses .zh").first());
    assert.equal(meaning.size, 18);
    assert.ok(meaning.family.includes("Mincho"));
    const example = await fontOf(page.locator(".entry .ex-zh").first());
    assert.equal(example.size, 14.5);
    assert.ok(example.family.includes("Noto Sans JP Variable"));
    const english = await fontOf(page.locator(".entry .headword"));
    assert.ok(english.family.includes("Atkinson Hyperlegible Next Variable"));
    // Protect an explicitly declared word face from global heading overrides.
    await page.evaluate(() => document.documentElement.removeAttribute("data-font"));
    const serifWord = await fontOf(page.locator(".entry .headword"));
    assert.ok(serifWord.family.startsWith('"Source Serif 4 Variable"'), "word headings preserve the original serif mode");
    await page.evaluate(() => document.documentElement.setAttribute("data-font", "sans"));
    assert.deepEqual(errors, []);
  });
}

test("Locale font CSS is deferred and a language switch waits for its stylesheet", { timeout: 60_000 }, async () => {
  const { page, errors } = await newPage({ locale: "zh-CN" });
  await page.goto(`${baseURL}#/atlas?view=grid`);
  await ready(page);
  assert.equal(await page.locator("html").getAttribute("lang"), "zh-CN");
  assert.deepEqual(await loadedFontLanguages(page), ["zh"]);
  const chinese = await fontOf(page.locator(".tile-zh").first());
  assert.ok(chinese.family.includes("Noto Sans SC Variable"));
  assert.ok(!chinese.family.includes("Noto Sans JP Variable"));

  let release;
  let requested;
  const delayed = new Promise((resolve) => { release = resolve; });
  const started = new Promise((resolve) => { requested = resolve; });
  await page.route(/\/language-font-ja-[^/]+\.css(?:\?|$)/, async (route) => {
    requested();
    await delayed;
    await route.continue();
  });
  await page.locator(".language-trigger").click();
  await page.getByRole("menuitemradio", { name: /日本語/ }).click();
  try {
    await Promise.race([started, delay(10_000).then(() => { throw new Error("Japanese font CSS was not requested"); })]);
    assert.equal(await page.locator("html").getAttribute("lang"), "zh-CN", "keep the existing language while its replacement CSS loads");
    assert.match(await page.locator(".atlas-head .display").innerText(), /看图学词/);
  } finally {
    release();
  }
  await page.locator('html[lang="ja"]').waitFor();
  await page.locator(".atlas-head .display").filter({ hasText: "絵で単語を学び" }).waitFor();
  await page.evaluate(() => document.fonts.ready);
  assert.deepEqual((await loadedFontLanguages(page)).sort(), ["ja", "zh"]);
  await audit(page, "Chinese to Japanese");
  assert.equal(await page.evaluate(() => document.fonts.check('500 15px "Noto Sans JP Variable"', "日本語")), true);
  await page.locator(".language-trigger").click();
  const chineseOption = page.getByRole("menuitemradio", { name: /中文/ });
  const menuFont = await fontOf(chineseOption);
  assert.ok(menuFont.family.includes("Noto Sans JP Variable"));
  assert.equal(menuFont.weight, "500");
  await chineseOption.click();
  await page.locator('html[lang="zh-CN"]').waitFor();
  await page.locator(".atlas-head .display").filter({ hasText: "看图学词" }).waitFor();
  assert.deepEqual((await loadedFontLanguages(page)).sort(), ["ja", "zh"]);
  assert.deepEqual(errors, []);
});

test("Fresh Japanese and other browser locales load only the Japanese font CSS", { timeout: 60_000 }, async () => {
  for (const locale of ["ja-JP", "en-US"]) {
    const { page, errors } = await newPage({ locale });
    await page.goto(`${baseURL}#/atlas?view=grid`);
    await ready(page);
    await audit(page, locale);
    assert.deepEqual(await loadedFontLanguages(page), ["ja"]);
    assert.deepEqual(errors, []);
  }
});

test("A failed locale stylesheet falls back and can be retried by reselecting the same language", { timeout: 60_000 }, async () => {
  const { page, errors } = await newPage({ locale: "zh-CN" });
  await page.goto(`${baseURL}#/atlas?view=grid`);
  await ready(page);
  let attempts = 0;
  await page.route(/\/language-font-ja-[^/]+\.css(?:\?|$)/, async (route) => {
    attempts++;
    if (attempts === 1) await route.abort("failed");
    else await route.continue();
  });

  await page.locator(".language-trigger").click();
  await page.getByRole("menuitemradio", { name: /日本語/ }).click();
  await page.locator('html[lang="ja"]').waitFor();
  await page.locator(".atlas-head .display").filter({ hasText: "絵で単語を学び" }).waitFor();
  assert.equal(attempts, 1);
  assert.deepEqual(await loadedFontLanguages(page), ["zh"]);
  assert.equal(await page.evaluate(() => [...document.fonts]
    .some((font) => font.family.includes("Noto Sans JP Variable"))), false);
  // A font request failure must leave the localized interface usable via fallbacks.
  assert.equal(await page.locator(".language-trigger").isVisible(), true);
  await page.getByRole("button", { name: "基礎 A2", exact: true }).click();
  assert.equal(await page.getByRole("button", { name: "基礎 A2", exact: true }).getAttribute("aria-pressed"), "true");

  await page.locator(".language-trigger").click();
  await page.getByRole("menuitemradio", { name: /日本語/ }).click();
  await page.waitForFunction(() => [...document.fonts]
    .some((font) => font.family.includes("Noto Sans JP Variable")));
  assert.equal(attempts, 2, "retry must issue a new request for the failed stylesheet");
  assert.deepEqual((await loadedFontLanguages(page)).sort(), ["ja", "zh"]);
  const faces = await page.evaluate(async () => {
    const fonts = await document.fonts.load('500 15px "Noto Sans JP Variable"', "日本語");
    return fonts.map((font) => ({ family: font.family, status: font.status }));
  });
  assert.ok(faces.length > 0, "the retried CSS must register real Japanese font faces");
  assert.ok(faces.every((font) => font.family.includes("Noto Sans JP Variable") && font.status === "loaded"));
  await audit(page, "recovered stylesheet");
  assert.deepEqual(errors, []);
});

test("A late font request cannot override the user's latest language selection", { timeout: 60_000 }, async () => {
  const { page, errors } = await newPage({ locale: "zh-CN" });
  await page.goto(`${baseURL}#/atlas?view=grid`);
  await ready(page);
  let release;
  let requested;
  const delayed = new Promise((resolve) => { release = resolve; });
  const started = new Promise((resolve) => { requested = resolve; });
  await page.route(/\/language-font-ja-[^/]+\.css(?:\?|$)/, async (route) => {
    requested();
    await delayed;
    await route.continue();
  });
  await page.locator(".language-trigger").click();
  await page.getByRole("menuitemradio", { name: /日本語/ }).click();
  try {
    await Promise.race([started, delay(10_000).then(() => { throw new Error("Japanese font CSS was not requested"); })]);
    await page.locator(".language-trigger").click();
    await page.getByRole("menuitemradio", { name: /中文/ }).click();
  } finally {
    release();
  }
  await page.waitForFunction(() => [...document.fonts]
    .some((font) => font.family.includes("Noto Sans JP Variable")));
  // Let the CSS promise and the React language effect both settle after load.
  await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  assert.equal(await page.locator("html").getAttribute("lang"), "zh-CN");
  assert.match(await page.locator(".atlas-head .display").innerText(), /看图学词/);
  assert.equal(await page.evaluate(() => localStorage.getItem("word-atlas:language")), "zh");
  assert.deepEqual(errors, []);
});
