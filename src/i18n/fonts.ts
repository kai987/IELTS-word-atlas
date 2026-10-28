import { getLanguage } from ".";

export const JAPANESE_FONT_FAMILY =
  '"Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif';
const WORD_FONT_FAMILY =
  '"WA Digits", "Atkinson Hyperlegible Next Variable", "Noto Sans SC Variable", "PingFang SC", "Microsoft YaHei", Georgia, serif';
const UI_FONT_FAMILY =
  '"WA Digits", "Atkinson Hyperlegible Next Variable", "Noto Sans SC Variable", -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif';
export const BRAND_FONT_FAMILY =
  '"Songti SC", "STSong", "Noto Serif SC", "Source Han Serif SC", serif';

/** Canvas text does not inherit the page's CSS font stack. */
export function getCanvasFonts() {
  const style = typeof document !== "undefined" && typeof getComputedStyle === "function"
    ? getComputedStyle(document.documentElement)
    : null;
  const japanese = getLanguage() === "ja";
  const japaneseText = `"WA Digits", "Atkinson Hyperlegible Next Variable", ${JAPANESE_FONT_FAMILY}`;
  return {
    serif: style?.getPropertyValue("--serif").trim() || (japanese ? japaneseText : WORD_FONT_FAMILY),
    sans: style?.getPropertyValue("--sans").trim() || (japanese ? japaneseText : UI_FONT_FAMILY),
    brand: style?.getPropertyValue("--brand").trim() || (japanese ? JAPANESE_FONT_FAMILY : BRAND_FONT_FAMILY),
  };
}
