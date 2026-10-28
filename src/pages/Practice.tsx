import { useI18n } from "../i18n";
import { Headphones, Keyboard, RotateCcw, Type } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { prefetch, useAtlas, useEntry } from "../atlas/context";
import type { Entry } from "../atlas/types";
import { play, stopAudio } from "../lib/audio";
import { cue } from "../lib/sound";
import { hashSeed, shuffle } from "../lib/text";
import { clean, correctCharacterCount, same, typingDelta, typingMetrics } from "../lib/typing";
import { store, useStore } from "../store/store";
import { AmbiencePicker } from "../ui/Ambience";
import { Illustration } from "../ui/Illustration";

type Mode = "word" | "sentence" | "dictation";
type Source = "recent" | "mistakes" | "saved" | "path";

export function Practice() {
  const { t } = useI18n();
  const MODES: [Mode, string, string, typeof Type][] = [
    ["word", t("单词", "単語"), t("看图写出单词", "絵を見て単語を入力"), Type],
    ["sentence", t("例句", "例文"), t("照着抄写，练出手感", "例文を書き写して入力に慣れる"), Keyboard],
    ["dictation", t("听写", "ディクテーション"), t("只听声音，写下整句", "音声だけを聞いて文全体を入力"), Headphones],
  ];
  const SOURCES: [Source, string][] = [
    ["recent", t("最近学过", "最近の学習")],
    ["mistakes", t("错词本", "間違えた単語")],
    ["saved", t("收藏", "お気に入り")],
    ["path", t("学习路线", "学習ルート")],
  ];
  const atlas = useAtlas();
  const progress = useStore((s) => s.progress);
  const startLevel = useStore((s) => s.settings.startLevel);
  const [mode, setMode] = useState<Mode>("word");
  const [source, setSource] = useState<Source>(() => (Object.keys(progress.cards).length ? "recent" : "path"));
  const [round, setRound] = useState<{ entries: Entry[]; key: number } | null>(null);

  const pool = useMemo(() => {
    const learned = Object.entries(progress.cards)
      .sort((a, b) => (b[1].last ?? 0) - (a[1].last ?? 0))
      .map(([id]) => id);
    const ids =
      source === "recent" ? learned : source === "mistakes" ? progress.mistakes : source === "saved" ? progress.bookmarks : atlas.words.filter((w) => w.cefr >= startLevel).slice(0, 400).map((w) => w.id);
    return ids.filter((id) => atlas.byId.has(id));
  }, [atlas, progress.cards, progress.mistakes, progress.bookmarks, source, startLevel]);

  const start = async () => {
    const ids = shuffle(pool.slice(0, 60), hashSeed(String(Date.now()))).slice(0, 10);
    const entries = (await prefetch(atlas, ids)).filter((e): e is Entry => !!e && (mode === "word" || e.ex.length > 0));
    if (entries.length) setRound({ entries, key: Date.now() });
  };

  if (round) return <TypingRound key={round.key} mode={mode} entries={round.entries} onExit={() => setRound(null)} onAgain={start} />;

  const best = progress.typing.filter((t) => t.mode === mode).reduce((m, t) => Math.max(m, t.wpm), 0);
  return (
    <div className="page practice">
      <header className="page-head">
        <p className="eyebrow">{t("练习 · Typing Studio", "練習 · Typing Studio")}</p>
        <h1 className="display">{t("让手，也记住它们。", "手でも、覚えよう。")}</h1>
        <p className="lede">{t("打字只练拼写和手感，不会改动记忆进度。", "タイピングでスペルと入力の感覚を練習します。記憶の学習状況には影響しません。")}</p>
      </header>
      <div className="practice-grid">
        <section className="panel">
          <h3 className="eyebrow">{t("模式", "モード")}</h3>
          <div className="mode-cards">
            {MODES.map(([k, name, desc, Icon]) => (
              <button key={k} className={`mode-card ${mode === k ? "is-on" : ""}`} onClick={() => setMode(k)} aria-pressed={mode === k}>
                <Icon size={22} strokeWidth={1.7} />
                <b>{name}</b>
                <small>{desc}</small>
              </button>
            ))}
          </div>
          <h3 className="eyebrow">{t("词来自", "出題元")}</h3>
          <div className="segmented segmented-wide">
            {SOURCES.map(([k, label]) => (
              <button key={k} className={source === k ? "is-on" : ""} onClick={() => setSource(k)} aria-pressed={source === k}>
                {label}
              </button>
            ))}
          </div>
          <p className="muted">
            {pool.length
              ? source === "path"
                ? t("从学习路线的前 400 个词里随机抽 10 个。", "学習ルートの最初の400語から、ランダムに10語を出題します。")
                : t(`可练 ${pool.length} 个词，每轮随机 10 个。`, `${pool.length}語を練習できます。毎回ランダムに10語を出題します。`)
              : t("这里还没有词，先去学几个，或换个来源。", "まだ単語がありません。先にいくつか学習するか、出題元を変えてください。")}
          </p>
          <button className="btn btn-primary btn-xl" onClick={start} disabled={!pool.length}>
            {t("开始一轮", "練習を始める")}
          </button>
        </section>
        <section className="panel practice-side">
          <img src={`${import.meta.env.BASE_URL}brand/${mode === "dictation" ? "listen" : "typing"}.webp`} alt="" />
          <dl className="mini-stats">
            <div>
              <dt>{t("最佳速度", "最高速度")}</dt>
              <dd>
                {best}
                <small>WPM</small>
              </dd>
            </div>
            <div>
              <dt>{t("完成轮次", "完了した回数")}</dt>
              <dd>{progress.typing.length}</dd>
            </div>
          </dl>
          <p className="muted">{t("WPM 按标准每 5 个字符计 1 词，只统计正确输入。", "WPMは5文字を1語として計算し、正しく入力した文字のみを数えます。")}</p>
        </section>
      </div>
    </div>
  );
}

function TypingRound({ mode, entries, onExit, onAgain }: { mode: Mode; entries: Entry[]; onExit: () => void; onAgain: () => void }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const settings = useStore((s) => s.settings);
  const [i, setI] = useState(0);
  const [value, setValue] = useState("");
  // Running totals live in a ref so every keystroke is counted exactly once.
  const totalsRef = useRef({ typed: 0, correct: 0, accepted: 0, ms: 0 });
  const [totals, setTotals] = useState(totalsRef.current);
  const [done, setDone] = useState(false);
  const started = useRef<number | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const e = entries[i];
  const { entry: localizedEntry, error: entryError } = useEntry(e.id);
  const currentEntry = atlas.peek(e.id) ?? localizedEntry;
  const pendingCue = entryError
    ? <span role="alert">{entryError}</span>
    : <span className="spinner" role="status" aria-label={t("正在加载释义…", "意味を読み込み中…")} />;
  const target = mode === "word" ? e.w : e.ex[0].en;

  useEffect(() => {
    setValue("");
    started.current = null;
    input.current?.focus();
    if (mode === "dictation") void play(atlas.audio(e, "ex"), e.ex[0].en, settings.accent);
    if (mode === "word" && settings.autoplay) void play(atlas.audio(e, settings.accent), e.w, settings.accent);
  }, [i]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => () => stopAudio(), []);

  const onChange = (next: string) => {
    if (done) return;
    if (started.current === null && next) started.current = performance.now();
    const d = typingDelta(value, next, target);
    if (settings.sfx && d.total > 0) void cue("key");
    const t = totalsRef.current;
    totalsRef.current = { ...t, typed: t.typed + d.total, correct: t.correct + d.correct };
    setTotals(totalsRef.current);
    setValue(next);
    if (clean(next).length >= clean(target).length && same(next.trimEnd(), target)) finishItem(next);
  };

  const finishItem = (final: string) => {
    const ms = started.current ? performance.now() - started.current : 0;
    const accepted = correctCharacterCount(final, target);
    if (settings.sfx) void cue("correct");
    const t = totalsRef.current;
    const nt = { ...t, accepted: t.accepted + accepted, ms: t.ms + ms };
    totalsRef.current = nt;
    setTotals(nt);
    if (i + 1 >= entries.length) {
      setDone(true);
      const m = typingMetrics(nt.correct, nt.typed, nt.accepted, nt.ms);
      store.progress((p) => ({ ...p, typing: [...p.typing, { at: Date.now(), mode, items: entries.length, wpm: m.wpm, accuracy: m.accuracy }].slice(-500) }));
    } else window.setTimeout(() => setI(i + 1), 260);
  };

  const m = typingMetrics(totals.correct, totals.typed, totals.accepted, totals.ms);
  const chars = Array.from(target);
  const typed = Array.from(value);

  if (done)
    return (
      <div className="page practice">
        <section className="panel typing-done">
          <p className="eyebrow">{t("本轮完成", "今回の練習が完了")}</p>
          <h1 className="display">
            {m.wpm} <small>WPM</small>
          </h1>
          <p className="lede">{t(`准确率 ${m.accuracy}% · ${entries.length} 项`, `正確率 ${m.accuracy}% · ${entries.length}問`)}</p>
          <div className="summary-actions">
            <button className="btn btn-ghost" onClick={onExit}>
              {t("返回", "戻る")}
            </button>
            <button className="btn btn-primary btn-xl" onClick={onAgain} autoFocus>
              <RotateCcw size={18} /> {t("再来一轮", "もう一度練習")}
            </button>
          </div>
        </section>
      </div>
    );

  return (
    <div className="page practice typing">
      <header className="typing-top">
        <button className="btn btn-ghost" onClick={onExit}>
          {t("结束", "終了")}
        </button>
        <AmbiencePicker />
        <div className="learn-progress">
          <span style={{ width: `${(i / entries.length) * 100}%` }} />
        </div>
        <span className="typing-meter">
          <b>{m.wpm}</b> WPM · <b>{m.accuracy}%</b>
        </span>
      </header>
      <section className="typing-stage" onClick={() => input.current?.focus()}>
        {mode === "word" && (
          <div className="typing-cue">
            <Illustration src={atlas.img(e)} word={e.w} topic={0} eager />
            <p>
              {currentEntry ? <><span className="pos">{currentEntry.senses[0].pos}</span> {currentEntry.senses[0].zh}</> : pendingCue}
            </p>
          </div>
        )}
        {mode !== "word" && (
          <p className="typing-zh">
            {mode === "dictation" && (
              <button className="link" onClick={() => play(atlas.audio(e, "ex"), e.ex[0].en, settings.accent)}>
                {t("再听一遍", "もう一度聞く")}
              </button>
            )}
            {currentEntry ? currentEntry.ex[0].zh : pendingCue}
          </p>
        )}
        <p className={`typing-text ${mode === "word" ? "is-word" : ""} ${mode === "dictation" ? "is-hidden" : ""}`} lang="en" aria-hidden="true">
          {chars.map((ch, k) => {
            const t = typed[k];
            const cls = t === undefined ? (k === typed.length ? "is-caret" : "") : same(t, ch) ? "is-ok" : "is-bad";
            const show = mode === "dictation" && t === undefined ? (ch === " " ? " " : /[A-Za-z]/.test(ch) ? "·" : ch) : ch;
            return (
              <span key={k} className={cls}>
                {show}
              </span>
            );
          })}
        </p>
        <input
          ref={input}
          className="typing-input"
          value={value}
          onChange={(ev) => onChange(ev.target.value)}
          autoFocus
          autoCapitalize="off"
          autoCorrect="off"
          autoComplete="off"
          spellCheck={false}
          aria-label={t("在这里输入", "ここに入力")}
        />
        <p className="muted typing-help">
          {mode === "dictation" ? t("听不清可以点「再听一遍」。", "聞き取れなければ「もう一度聞く」を押してください。") : t("直接开始输入，全部正确后自动进入下一项。", "そのまま入力してください。すべて正しく入力すると自動で次へ進みます。")} {t(`第 ${i + 1}/${entries.length} 项`, `${i + 1}/${entries.length}問目`)}
        </p>
      </section>
    </div>
  );
}
