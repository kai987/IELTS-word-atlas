import { getLanguage } from ".";

export const JAPANESE_FONT_FAMILY =
  '"Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif';

/** Canvas text does not inherit the page's CSS font stack. */
export function getCanvasFonts() {
  if (getLanguage() === "ja") {
    return {
      serif: `"Fraunces Variable", ${JAPANESE_FONT_FAMILY}`,
      sans: JAPANESE_FONT_FAMILY,
    };
  }
  return {
    serif:
      '"Fraunces Variable", "Hiragino Mincho ProN", "Yu Mincho", "Songti SC", "Noto Serif SC", Georgia, serif',
    sans: '-apple-system, "Hiragino Kaku Gothic ProN", "Yu Gothic", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif',
  };
}
