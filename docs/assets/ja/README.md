# 日本語版の紹介メディア

このフォルダーには、READMEで使用する日本語のバナー、画面キャプチャ、紹介動画を収録しています。元の中国語版メディアは、一つ上のフォルダーに残しています。

- `banner.jpg`：日本語の見出しと元プロジェクトのイラストを組み合わせたバナー。制作元は [`scripts/media/ja-banner.html`](../../../scripts/media/ja-banner.html) です。
- `today-*`・`atlas-*`・`word-*`・`galaxy.jpg`：実際の日本語画面。デスクトップは1440×900、スマートフォンは390×844で撮影しました。星図の640語は撮影用のデモデータです。利用者の学習実績ではありません。
- `launch.mp4`：約45秒の日本語紹介動画。BGMと日本語の起動メッセージを使用。
- `demo.mp4`：約28秒の日本語画面ガイド。音声はBGMのみ。
- `launch-preview.webp`・`launch-poster.jpg`：紹介動画のアニメーションプレビューと静止画。

動画は画面キャプチャとイラストに、日本語字幕、緩やかなズーム、クロスフェードを加えて再制作しています。操作を連続録画した動画ではありません。英文・英単語は学習教材として保持しています。

両動画の音楽は `public/sfx/amb-stars.mp3` です。紹介動画だけに使用する短い起動メッセージは `public/sfx/splash-voice-ja-morioki.mp3`（AivisSpeech・morioki）です。中国語のナレーションは使用していません。全編の日本語ナレーションは含みません。

## 再制作

アプリを日本語に切り替えて上記の画面をキャプチャし、同じ名前で保存します。ブラウザー拡張のフローティングボタンは撮影時に隠しています。アプリ自体の文言や学習内容は変更していません。

バナーは開発サーバーで `/scripts/media/ja-banner.html` を開き、1600×720でキャプチャできます。

Python 3、Pillow（アニメーションWebP対応）、ffmpeg（libx264）、日本語フォントを準備して実行します。

```sh
python3 scripts/render-japanese-media.py
```

macOS以外で日本語フォントを指定する場合は `ATLAS_JA_FONT` を設定してください。

## クレジット

元のイラスト・アプリの制作： [designfuchen/word-atlas](https://github.com/designfuchen/word-atlas) / Word Atlas contributors。

日本語化、画面キャプチャ、動画の再構成： [kai987/IELTS-word-atlas](https://github.com/kai987/IELTS-word-atlas)。元の素材に日本語の字幕・配置・画面を追加しています。単語コンテンツとイラストの利用条件は [CC BY 4.0](../../../CONTENT_LICENSE.md)、コードは [MIT](../../../LICENSE) を参照してください。
