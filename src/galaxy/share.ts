import { translate as t } from "../i18n";
import { getCanvasFonts } from "../i18n/fonts";
import { toast } from "../ui/Toast";

/** "My word galaxy": the live render framed as a 4:5 poster. */
export async function shareGalaxy(source: HTMLCanvasElement, lit: number, total: number) {
  const { serif: SERIF, sans: SANS } = getCanvasFonts();
  try {
    const W = 1080;
    const H = 1350;
    const c = document.createElement("canvas");
    c.width = W;
    c.height = H;
    const g = c.getContext("2d")!;
    const cardText = t(
      "我的词汇星图 已点亮颗星 共个雅思词 每学会一个，就点亮一颗 词光 一词一画，点亮雅思",
      "わたしの単語星図 個の星を灯しました IELTS単語 全語 覚えた単語が星になる 詞光 単語と絵で、IELTSを照らす",
    ) + " 0123456789 Word Atlas";
    await Promise.all([
      document.fonts.load(`600 72px ${SERIF}`, cardText),
      document.fonts.load(`400 28px ${SANS}`, cardText),
    ]).catch(() => null);
    g.fillStyle = "#090c18";
    g.fillRect(0, 0, W, H);
    // Cover-fit the galaxy into the upper part of the poster.
    const box = { x: 0, y: 0, w: W, h: 1020 };
    const s = Math.max(box.w / source.width, box.h / source.height);
    const sw = box.w / s;
    const sh = box.h / s;
    g.drawImage(source, (source.width - sw) / 2, (source.height - sh) / 2, sw, sh, box.x, box.y, box.w, box.h);
    const fade = g.createLinearGradient(0, 760, 0, 1080);
    fade.addColorStop(0, "rgba(9,12,24,0)");
    fade.addColorStop(1, "rgba(9,12,24,1)");
    g.fillStyle = fade;
    g.fillRect(0, 760, W, 330);
    const pad = 72;
    g.fillStyle = "rgba(243,236,223,.62)";
    g.font = `500 28px ${SANS}`;
    g.fillText(t("我的词汇星图", "わたしの単語星図"), pad, 1110);
    g.fillStyle = "#f3ecdf";
    g.font = `600 76px ${SERIF}`;
    g.fillText(t(`已点亮 ${lit.toLocaleString()} 颗星`, `${lit.toLocaleString()} 個の星を灯しました`), pad, 1196, W - pad * 2);
    g.font = `400 28px ${SANS}`;
    g.fillStyle = "rgba(243,236,223,.6)";
    g.fillText(t(`共 ${total.toLocaleString()} 个雅思词 · 每学会一个，就点亮一颗`, `IELTS単語 全 ${total.toLocaleString()} 語 · 覚えた単語が星になる`), pad, 1248, W - pad * 2);
    g.fillStyle = "rgba(243,236,223,.16)";
    g.fillRect(pad, H - 66, W - pad * 2, 1);
    g.fillStyle = "#f3ecdf";
    g.font = `600 30px ${SERIF}`;
    g.fillText(t("词光 · Word Atlas", "詞光 · Word Atlas"), pad, H - 26);
    g.font = `400 24px ${SANS}`;
    g.fillStyle = "rgba(243,236,223,.55)";
    const tag = t("一词一画，点亮雅思", "単語と絵で、IELTSを照らす");
    g.fillText(tag, W - pad - g.measureText(tag).width, H - 28);
    const blob = await new Promise<Blob | null>((r) => c.toBlob(r, "image/png"));
    if (!blob) throw new Error("no blob");
    const file = new File([blob], "word-atlas-galaxy.png", { type: "image/png" });
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file] }).catch(() => null);
      return;
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = file.name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    toast(t("星图已保存", "星図を保存しました"), "ok");
  } catch {
    toast(t("星图生成失败", "星図を作成できませんでした"), "warn");
  }
}
