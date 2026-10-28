import { useI18n } from "../i18n";
import { ArrowUpRight, Database, Github, Heart } from "lucide-react";
import { useAtlas } from "../atlas/context";
import { REPO_URL } from "../config";

const BASE = import.meta.env.BASE_URL;

export function About() {
  const { t } = useI18n();
  const atlas = useAtlas();
  return (
    <div className="page about">
      <header className="about-hero">
        <img src={`${BASE}brand/og.webp`} alt="" />
        <div>
          <p className="eyebrow">{t("关于词光", "詞光について")}</p>
          <h1 className="display">{t("一词一画，点亮雅思。", "単語と絵で、IELTSに光を。")}</h1>
          <p className="lede">
            {t(`词光把雅思阅读 8000 词整理成 ${atlas.count.toLocaleString()} 个词条。每个词一幅原创插画，一句日常例句，一句雅思例句，配英美发音、常用搭配和易混提示。学会一个，就在你的星图上点亮一颗星。`, `詞光はIELTSリーディング向けの8000語を、${atlas.count.toLocaleString()}件の見出し語にまとめました。各単語にオリジナルのイラスト、日常の例文とIELTSの例文を一つずつ収録し、イギリス・アメリカ英語の発音、コロケーション、混同しやすい語のヒントを添えています。一語覚えるたびに、あなたの星図に星が一つ灯ります。`)}
          </p>
          <p className="lede">{t("它免费、开源、无需注册。代码用 MIT，词库用 CC BY 4.0，谁都可以拿去用。", "無料・オープンソースで、登録も不要です。コードはMIT、単語データはCC BY 4.0ライセンスで、どなたでも利用できます。")}</p>
          <div className="about-actions">
            <a className="btn btn-primary" href={REPO_URL} target="_blank" rel="noreferrer">
              <Github size={18} /> {t("在 GitHub 上查看", "GitHubで見る")}
            </a>
            <a className="btn btn-ghost" href={`${REPO_URL}/tree/main/data`} target="_blank" rel="noreferrer">
              <Database size={18} /> {t("下载词库 JSON / CSV", "単語データをダウンロード JSON / CSV")}
            </a>
          </div>
        </div>
      </header>

      <div className="about-grid">
        <section className="panel">
          <h3 className="eyebrow">{t("为什么记得住", "記憶に残る理由")}</h3>
          <ul className="feature-list">
            <li>
              <b>{t("先看见。", "まずは見る。")}</b>{t("每个词都有一幅画，画的就是第一句例句里发生的事。", "どの単語にも、最初の例文の場面を描いた絵があります。")}
            </li>
            <li>
              <b>{t("再想起。", "次に思い出す。")}</b>{t("选义、看图补句、听音辨词、拼写，从认得走到会写。", "意味の選択、絵を見て文を完成、音から単語を選択、スペル入力を通して、わかる単語を自分で書ける単語にしていきます。")}
            </li>
            <li>
              <b>{t("刚好在快忘时重逢。", "忘れかけた頃に、もう一度。")}</b>{t("FSRS 是新版 Anki 用的开源记忆算法，只在你快要遗忘时安排复习。", "FSRSは新しいAnkiでも採用されているオープンソースの記憶アルゴリズムです。忘れかけるタイミングに合わせて復習を設定します。")}
            </li>
            <li>
              <b>{t("分数诚实。", "正答率を正確に。")}</b>{t("只算第一次作答。答错的词会换个题型再见一面，但不会抬高正确率。", "正答率は最初の解答だけで計算します。間違えた単語は別の形式で再登場しますが、正答率には加算されません。")}
            </li>
            <li>
              <b>{t("进度只属于你。", "学習データは、あなたのもの。")}</b>{t("没有账号，没有服务器，数据存在你的浏览器里，随时能导出。", "アカウントもサーバーも不要です。データはブラウザーに保存され、いつでもエクスポートできます。")}
            </li>
          </ul>
        </section>

        <section className="panel">
          <h3 className="eyebrow">{t("快捷键", "キーボードショートカット")}</h3>
          <dl className="keys">
            <div>
              <dt>
                <kbd>⌘</kbd>
                <kbd>K</kbd> {t("或", "または")} <kbd>/</kbd>
              </dt>
              <dd>{t("搜索任何词", "単語を検索")}</dd>
            </div>
            <div>
              <dt>
                <kbd>1</kbd>–<kbd>4</kbd>
              </dt>
              <dd>{t("选择答案", "解答を選択")}</dd>
            </div>
            <div>
              <dt>
                <kbd>Enter</kbd>
              </dt>
              <dd>{t("确认 / 继续", "確定 / 続ける")}</dd>
            </div>
            <div>
              <dt>
                <kbd>←</kbd> <kbd>→</kbd>
              </dt>
              <dd>{t("词卡里切换上一个、下一个", "単語カードを前後に切り替える")}</dd>
            </div>
            <div>
              <dt>
                <kbd>Esc</kbd>
              </dt>
              <dd>{t("关闭弹窗", "ダイアログを閉じる")}</dd>
            </div>
          </dl>
        </section>

        <section className="panel">
          <h3 className="eyebrow">{t("内容从哪里来", "コンテンツについて")}</h3>
          <p className="muted">
            {t("释义、例句、搭配和提示由大语言模型按统一的词典规范重新撰写；插画由图像模型按统一画风逐词绘制；发音和朗读由 ElevenLabs 合成（英音 Alice，美音 Sarah）。所有内容都经过结构和一致性的自动校验，但没有逐条人工审校。看到错的地方，欢迎在 GitHub 提 Issue，或者直接改数据提 PR。", "意味・例文・コロケーション・ヒントは、統一した辞書基準に沿って大規模言語モデルが新たに作成しました。イラストは画像生成モデルで画風を統一して単語ごとに制作し、発音・読み上げはElevenLabsで合成しています（イギリス英語：Alice、アメリカ英語：Sarah）。すべての内容に構造と整合性の自動検証を行っていますが、一件ずつの人手による校閲は行っていません。誤りにお気づきの際は、GitHubのIssue、またはデータを修正したPRでお知らせください。")}
          </p>
          <p className="muted">{t("词光不是官方雅思词表，也不承诺提分。它只想把背单词这件事，做得好看一点、扎实一点。", "詞光はIELTS公式の単語リストではなく、スコア向上を保証するものでもありません。単語を覚える時間を、少し美しく、着実なものにするためのツールです。")}</p>
        </section>

        <section className="panel">
          <h3 className="eyebrow">{t("给开发者", "開発者の方へ")}</h3>
          <p className="muted">
            <code>data/word-atlas.json</code> {t("和", "と")} <code>.csv</code> {t("是完整词库；", "は単語データの全件版です。")}<code>public/atlas</code> {t("里是网页用的分块数据、插画和音频。拿去做 Anki 牌组、背词小程序、浏览器插件，或者 AI 应用的评测集，署名即可。", "にはウェブ用に分割したデータ・イラスト・音声が入っています。クレジットを表示すれば、Ankiデッキ、単語学習アプリ、ブラウザー拡張、AIアプリの評価用データなどに利用できます。")}
          </p>
          <a className="link" href={`${REPO_URL}#readme`} target="_blank" rel="noreferrer">
            {t("阅读文档", "ドキュメントを読む")} <ArrowUpRight size={14} />
          </a>
        </section>
      </div>
      <p className="colophon">
        <Heart size={14} /> {t("做给每一个在背单词的人。", "単語を覚えるすべての人へ。")}
      </p>
    </div>
  );
}
