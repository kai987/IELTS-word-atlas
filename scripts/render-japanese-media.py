#!/usr/bin/env python3
"""Render the Japanese README films from Japanese UI captures and licensed assets.

Requires Python 3, Pillow (animated WebP support), ffmpeg (libx264), and a Japanese font.
Run after capturing docs/assets/ja/{banner,today-desktop,atlas-desktop,
word-desktop,galaxy}.jpg:

    python3 scripts/render-japanese-media.py

Set ATLAS_JA_FONT to a Japanese Mincho/serif font on non-macOS systems.
The original Chinese media are never read as video or overwritten.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 1280, 720
NAVY = "#111728"
CREAM = "#f5eedf"
GOLD = "#e8b65a"
RUST = "#bf5638"


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def font_file() -> str:
    explicit = os.environ.get("ATLAS_JA_FONT")
    if explicit:
        return explicit
    patterns = [
        "/System/Library/Fonts/*明朝*ProN*",
        "/usr/share/fonts/**/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/**/NotoSerifJP-Regular.ttf",
    ]
    for pattern in patterns:
        found = glob.glob(pattern, recursive=True)
        if found:
            return found[0]
    raise SystemExit("Japanese font missing; set ATLAS_JA_FONT.")


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str,
         size: int, fill: str = CREAM, anchor: str = "la") -> None:
    draw.text(xy, value, font=ImageFont.truetype(FONT, size), fill=fill, anchor=anchor)


def fitted(path: Path, bounds: tuple[int, int]) -> Image.Image:
    return ImageOps.contain(Image.open(path).convert("RGB"), bounds,
                            Image.Resampling.LANCZOS)


def screenshot_scene(assets: Path, filename: str, title: str,
                     eyebrow: str, subtitle: str) -> Image.Image:
    image = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(image)
    text(draw, (62, 28), eyebrow, 17, GOLD)
    text(draw, (62, 55), title, 36)
    shot = fitted(assets / filename, (1156, 520))
    x, y = (W - shot.width) // 2, 126 + (520 - shot.height) // 2
    image.paste(shot, (x, y))
    draw.rounded_rectangle((x - 1, y - 1, x + shot.width, y + shot.height),
                           radius=7, outline="#4a5267", width=1)
    text(draw, (W // 2, 673), subtitle, 18, "#c2c6d0", "mm")
    return image


def banner_scene(assets: Path) -> Image.Image:
    image = Image.new("RGB", (W, H), CREAM)
    banner = fitted(assets / "banner.jpg", (W, 614))
    image.paste(banner, ((W - banner.width) // 2, 30 + (614 - banner.height) // 2))
    draw = ImageDraw.Draw(image)
    text(draw, (W // 2, 665), "日本語で学べる、7,298語のIELTS単語図鑑。", 25, NAVY, "mm")
    return image


def illustration_scene() -> Image.Image:
    image = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    text(draw, (64, 35), "一語に一枚の絵。", 46, NAVY)
    text(draw, (65, 105), "例文の場面が、記憶の手がかりになる。", 23, RUST)
    words = [("abandon", "置き去りにする"), ("volcano", "火山"),
             ("orchestra", "オーケストラ"), ("telescope", "望遠鏡")]
    for i, (word, meaning) in enumerate(words):
        x = 64 + i * 292
        pic = Image.open(ROOT / "public/atlas/img" / f"{word}.webp").convert("RGB")
        pic = ImageOps.fit(pic, (272, 304), method=Image.Resampling.LANCZOS)
        image.paste(pic, (x, 207))
        text(draw, (x, 530), word, 31, NAVY)
        text(draw, (x, 580), meaning, 21, RUST)
    text(draw, (64, 662), "7,298枚のイラスト · 14,596の英語例文", 20, "#62687a")
    return image


def closing_scene() -> Image.Image:
    image = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(image)
    text(draw, (W // 2, 116), "詞光", 82, CREAM, "mm")
    text(draw, (W // 2, 203), "W O R D   A T L A S", 27, GOLD, "mm")
    text(draw, (W // 2, 317), "無料。登録不要。", 52, CREAM, "mm")
    text(draw, (W // 2, 401), "意味・例文・学習ヒントを、日本語で。", 29, CREAM, "mm")
    text(draw, (W // 2, 472), "英・米の発音  /  FSRS間隔反復  /  学習データは端末に保存", 22, GOLD, "mm")
    draw.line((246, 550, 1034, 550), fill="#4a5267", width=1)
    text(draw, (W // 2, 602), "kai987.github.io/IELTS-word-atlas/", 27, CREAM, "mm")
    text(draw, (W // 2, 665), "原作：Word Atlas contributors · 日本語版：kai987/IELTS-word-atlas", 16,
         "#b2bacd", "mm")
    return image


def encode_film(tmp: Path, name: str, images: list[Path], duration: float,
                assets: Path, fps: int, include_welcome: bool) -> float:
    clips: list[Path] = []
    for i, scene in enumerate(images):
        clip = tmp / f"{name}-{i}.mp4"
        frames = round(duration * fps)
        # A restrained push-in gives the still UI captures motion while preserving readability.
        vf = (f"scale=2560:1440,zoompan=z='1+0.014*on/{frames}':"
              f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:"
              f"s={W}x{H}:fps={fps},setsar=1,format=yuv420p")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(scene), "-vf", vf,
             "-frames:v", str(frames), "-an", "-c:v", "libx264", "-crf", "21",
             "-preset", "fast", "-threads", "4", str(clip)])
        clips.append(clip)
    transition = 0.45
    length = len(clips) * duration - (len(clips) - 1) * transition
    args = ["ffmpeg", "-y", "-loglevel", "error", "-filter_complex_threads", "1"]
    for clip in clips:
        args += ["-i", str(clip)]
    music_index = len(clips)
    args += ["-i", str(ROOT / "public/sfx/amb-stars.mp3")]
    filters: list[str] = []
    prev = "0:v"
    for i in range(1, len(clips)):
        label = f"v{i}"
        offset = i * (duration - transition)
        filters.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={transition}:offset={offset:.3f}[{label}]")
        prev = label
    filters.append(f"[{music_index}:a]atrim=duration={length:.3f},asetpts=PTS-STARTPTS,"
                   f"volume=0.18,afade=t=in:d=0.8,afade=t=out:st={length-1.7:.3f}:d=1.7[music]")
    audio = "music"
    if include_welcome:
        args += ["-i", str(ROOT / "public/sfx/splash-voice-ja-morioki.mp3")]
        filters.append(f"[{music_index+1}:a]adelay=800:all=1,volume=1.0[voice]")
        filters.append("[music][voice]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[audio]")
        audio = "audio"
    args += ["-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-map", f"[{audio}]",
             "-t", f"{length:.3f}", "-r", str(fps), "-c:v", "libx264", "-crf", "21",
             "-preset", "medium", "-threads", "4", "-pix_fmt", "yuv420p", "-c:a", "aac",
             "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(assets / f"{name}.mp4")]
    run(args)
    return length


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", type=Path, default=ROOT / "docs/assets/ja")
    parser.add_argument("--fps", type=int, default=30)
    opts = parser.parse_args()
    assets = opts.assets_dir.resolve()
    required = ["banner.jpg", "today-desktop.jpg", "atlas-desktop.jpg", "word-desktop.jpg", "galaxy.jpg"]
    missing = [name for name in required if not (assets / name).is_file()]
    if missing:
        raise SystemExit("Capture the Japanese UI first; missing: " + ", ".join(missing))
    with tempfile.TemporaryDirectory(prefix="atlas-ja-media-") as td:
        tmp = Path(td)
        scenes = [
            banner_scene(assets),
            illustration_scene(),
            screenshot_scene(assets, "today-desktop.jpg", "毎日の学習を、少しずつ。", "01 / 今日", "復習してから、新しい単語へ。"),
            screenshot_scene(assets, "word-desktop.jpg", "意味も、例文も、日本語で。", "02 / 単語カード", "英・米の発音と、コロケーション、学習ヒント。"),
            screenshot_scene(assets, "atlas-desktop.jpg", "絵から広がる、単語の図鑑。", "03 / 図鑑", "CEFR A1–C2 · IELTSの19トピック"),
            screenshot_scene(assets, "galaxy.jpg", "覚えた一語が、星になる。", "04 / 単語の星図", "7,298語が、7,298個の星に。  ※デモデータ"),
            screenshot_scene(assets, "today-desktop.jpg", "忘れかけた頃に、もう一度。", "05 / 間隔反復", "FSRSで復習。最初の解答だけを、正答率に記録。"),
            closing_scene(),
        ]
        paths = []
        for i, scene in enumerate(scenes):
            p = tmp / f"scene-{i}.png"
            scene.save(p)
            paths.append(p)
        launch_len = encode_film(tmp, "launch", paths, 6.0, assets, opts.fps, True)
        demo_len = encode_film(tmp, "demo", [paths[i] for i in [0, 2, 3, 4, 5, 7]],
                               5.0, assets, opts.fps, False)
        scenes[0].save(assets / "launch-poster.jpg", quality=93)
        # 12 s preview samples four complete Japanese scenes from the finished film.
        preview_filter = ("[0:v]split=4[s0][s1][s2][s3];"
                          "[s0]trim=start=0:duration=3,setpts=PTS-STARTPTS[a];"
                          "[s1]trim=start=11.1:duration=3,setpts=PTS-STARTPTS[b];"
                          "[s2]trim=start=22.2:duration=3,setpts=PTS-STARTPTS[c];"
                          "[s3]trim=start=38.85:duration=3,setpts=PTS-STARTPTS[d];"
                          "[a][b][c][d]concat=n=4:v=1:a=0,fps=8,scale=800:-2[v]")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(assets / "launch.mp4"),
             "-filter_complex", preview_filter, "-map", "[v]", "-an", "-q:v", "2",
             str(tmp / "preview-%03d.jpg")])
        preview_frames = [Image.open(p).convert("RGB") for p in sorted(tmp.glob("preview-*.jpg"))]
        preview_frames[0].save(assets / "launch-preview.webp", format="WEBP", save_all=True,
                               append_images=preview_frames[1:], duration=125, loop=0,
                               quality=65, method=4)
        print(json.dumps({"launchSeconds": launch_len, "demoSeconds": demo_len,
                          "previewSeconds": 12, "resolution": [W, H],
                          "font": FONT, "output": str(assets)}, ensure_ascii=False))


if __name__ == "__main__":
    FONT = font_file()
    main()
