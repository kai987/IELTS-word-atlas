/**
 * Read-only DOM audit shared by browser QA and the production typography tests.
 * Keep this function self-contained so it can be passed to page.evaluate().
 */
export function auditTypography() {
  const root = document.documentElement;
  const japanese = /^ja(?:-|$)/i.test(root.lang);
  const samples = [];
  for (const element of document.querySelectorAll("body *")) {
    if (!element.getClientRects().length) continue;
    const style = getComputedStyle(element);
    if (style.visibility !== "visible") continue;
    const language = element.closest("[lang]")?.getAttribute("lang") || root.lang;
    if (!/^ja(?:-|$)/i.test(language)) continue;
    const text = [...element.childNodes]
      .filter((node) => node.nodeType === 3)
      .map((node) => node.textContent || "")
      .join("")
      .trim();
    if (!/[\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}]/u.test(text)) continue;
    samples.push({
      tag: element.tagName.toLowerCase(),
      classes: element.getAttribute("class") || "",
      text: text.slice(0, 80),
      size: +style.fontSize.slice(0, -2),
      family: style.fontFamily,
      weight: style.fontWeight,
      lineHeight: style.lineHeight,
      color: style.color,
    });
  }
  const smallJapanese = samples.filter((sample) => sample.size <= 15);
  return {
    language: root.lang,
    viewport: { width: root.clientWidth, height: root.clientHeight },
    // Fixed layers can span the scrollbar gutter without overflowing the viewport.
    horizontalOverflow: Math.max(0, root.scrollWidth - innerWidth),
    smallJapanese,
    largeJapanese: samples.filter((sample) => sample.size > 15),
    violations: japanese
      ? smallJapanese.filter((sample) => !sample.family.includes("Noto Sans JP Variable"))
      : [],
  };
}

/** Validate the same JSON report collected by Playwright or a CUA DOM audit. */
export function typographyReportErrors(report) {
  const errors = [];
  if (report?.language !== "ja") errors.push("Expected a Japanese document");
  if (!Array.isArray(report?.smallJapanese) || report.smallJapanese.length === 0) {
    errors.push("No small Japanese text was audited");
  } else {
    for (const sample of report.smallJapanese) {
      if (!(sample.size > 0 && sample.size <= 15)) {
        errors.push(`Invalid small-text size: ${sample.text}`);
      }
      if (!sample.family?.includes("Noto Sans JP Variable")) {
        errors.push(`Small Japanese text does not use the UI face: ${sample.text}`);
      }
    }
  }
  if (!(report?.horizontalOverflow <= 1)) errors.push("Horizontal page overflow");
  return errors;
}
