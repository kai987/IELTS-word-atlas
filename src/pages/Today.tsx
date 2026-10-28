import { useI18n } from "../i18n";
import { ArrowRight, Flame, Keyboard, Sparkles } from "lucide-react";
import { useEffect, useMemo } from "react";
import { prefetch, useAtlas, useEntry } from "../atlas/context";
import { go, openWord } from "../lib/router";
import { cue } from "../lib/sound";
import { hashSeed } from "../lib/text";
import { buildSession, masteredCount, todayPlan } from "../store/session";
import { isMastered } from "../store/srs";
import { dayKey, store, useStore } from "../store/store";
import { Galaxy } from "../galaxy/Galaxy";
import { Highlight, Pronounce } from "../ui/EntryView";
import { Illustration } from "../ui/Illustration";
import { Ring } from "../ui/Ring";

const BRAND = `${import.meta.env.BASE_URL}brand`;

function greeting(h: number, t: (zh: string, ja: string) => string) {
  if (h < 5) return t("夜深了", "夜も更けましたね");
  if (h < 11) return t("早上好", "おはようございます");
  if (h < 14) return t("中午好", "こんにちは");
  if (h < 18) return t("下午好", "こんにちは");
  return t("晚上好", "こんばんは");
}

export function streakOf(days: Record<string, { r: number }>) {
  let n = 0;
  const d = new Date();
  if (!(days[dayKey(d)]?.r > 0)) d.setDate(d.getDate() - 1);
  while (days[dayKey(d)]?.r > 0) {
    n++;
    d.setDate(d.getDate() - 1);
  }
  return n;
}

export function Today() {
  const { t, language } = useI18n();
  const atlas = useAtlas();
  const progress = useStore((s) => s.progress);
  const settings = useStore((s) => s.settings);
  const plan = useMemo(() => todayPlan(atlas, progress, settings), [atlas, progress, settings]);
  // Warm the first cards of today's journey so the session opens instantly.
  const firstIds = [...plan.due.slice(0, 4), ...plan.fresh.slice(0, 6)].join(",");
  useEffect(() => {
    const ids = firstIds.split(",").filter(Boolean);
    const t = window.setTimeout(() => void prefetch(atlas, ids), 800);
    return () => window.clearTimeout(t);
  }, [atlas, firstIds]);
  const now = new Date();
  const today = progress.days[dayKey()];
  const streak = streakOf(progress.days);
  const active = progress.session && !progress.session.finished ? progress.session : null;
  const total = plan.due.length + plan.fresh.length;
  const goal = settings.dailyNew + Math.min(plan.due.length, 60);
  const doneToday = today?.r ?? 0;

  const start = (opts?: { reviewOnly?: boolean; extra?: number }) => {
    if (!active) {
      const s = buildSession(atlas, progress, opts?.extra ? { ...settings, dailyNew: (today?.n ?? 0) + opts.extra } : settings, { reviewOnly: opts?.reviewOnly });
      if (!s.steps.length) return;
      store.progress((p) => ({ ...p, session: s }));
    }
    if (settings.sfx) void cue("start");
    go({ page: "learn" });
  };

  const week = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    const k = dayKey(d);
    return { k, label: t("日一二三四五六", "日月火水木金土")[d.getDay()], v: progress.days[k]?.r ?? 0, today: i === 6 };
  });

  const learned = Object.keys(progress.cards).length;
  const mastered = masteredCount(progress);
  const teaser = (active ? active.newIds : plan.fresh).slice(0, 5).map((id) => atlas.byId.get(id)!).filter(Boolean);

  return (
    <div className="page today">
      <header className="greet">
        <p className="eyebrow">
          {t(`${now.getMonth() + 1}月${now.getDate()}日 · 星期${"日一二三四五六"[now.getDay()]}`, `${now.getMonth() + 1}月${now.getDate()}日 · ${"日月火水木金土"[now.getDay()]}曜日`)}
        </p>
        <h1 className="display">
          {language === "ja" ? <><span className="greeting-segment">{greeting(now.getHours(), t)}、</span><wbr /><span className="greeting-segment">探検家さん。</span></> : `${greeting(now.getHours(), t)}，探索者。`}
        </h1>
      </header>

      <section className={`journey ${total === 0 && !active ? "is-clear" : ""}`}>
        <img className="journey-art" src={`${BRAND}/hero.webp`} alt="" fetchPriority="high" />
        <div className="journey-body">
          {active ? (
            <>
              <p className="eyebrow eyebrow-light">{t("旅程进行中", "学習の途中です")}</p>
              <h2>
                {t("还剩", "残り")} <b>{active.steps.length - active.index}</b> {t("步", "ステップ")}
              </h2>
              <p className="journey-lede">{t("进度已保存，随时接着走。", "進捗は保存済み。いつでも続きを始められます。")}</p>
            </>
          ) : total > 0 ? (
            <>
              <p className="eyebrow eyebrow-light">{t("今日旅程", "今日の学習")}</p>
              <h2>
                {plan.due.length > 0 && (
                  <>
                    {t("复习", "復習")} <b>{plan.due.length}</b>{t("", "語")}
                  </>
                )}
                {plan.due.length > 0 && plan.fresh.length > 0 && <i> · </i>}
                {plan.fresh.length > 0 && (
                  <>
                    {t("新词", "新しい単語")} <b>{plan.fresh.length}</b>{t("", "語")}
                  </>
                )}
              </h2>
              <p className="journey-lede">{t(`约 ${plan.minutes} 分钟。先温故，再知新。`, `約${plan.minutes}分。復習してから、新しい単語へ。`)}</p>
            </>
          ) : (
            <>
              <p className="eyebrow eyebrow-light">{t("今日已完成", "今日の学習は完了")}</p>
              <h2>{t("今天的星，都亮了。", "今日の星が、すべて灯りました。")}</h2>
              <p className="journey-lede">{t("记忆需要一点留白。想多走一段，也可以。", "記憶には少しの休息も必要です。もう少し学びたければ、続けることもできます。")}</p>
            </>
          )}
          {teaser.length > 0 && (
            <div className="teaser" aria-label={t("今天将遇见的新词", "今日出会う新しい単語")}>
              {teaser.map((w, i) => (
                <Illustration key={w.id} src={atlas.img(w, "thumb")} word={w.word} topic={w.topic} className={`teaser-${i}`} />
              ))}
              <span>{t("今天会遇见它们", "今日出会う単語")}</span>
            </div>
          )}
          <div className="journey-actions">
            {active || total > 0 ? (
              <button className="btn btn-primary btn-xl" onClick={() => start()}>
                {active ? t("继续旅程", "学習を再開") : t("开始今天的旅程", "今日の学習を始める")} <ArrowRight size={20} />
              </button>
            ) : (
              <button className="btn btn-primary btn-xl" onClick={() => start({ extra: 5 })}>
                {t("再认识 5 个新词", "さらに5語を学ぶ")} <Sparkles size={18} />
              </button>
            )}
            {!active && plan.due.length > 0 && plan.fresh.length > 0 && (
              <button className="btn btn-glass" onClick={() => start({ reviewOnly: true })}>
                {t("只复习", "復習のみ")}
              </button>
            )}
            {!active && total === 0 && (
              <button className="btn btn-glass" onClick={() => go({ page: "practice" })}>
                <Keyboard size={18} /> {t("打字练习", "タイピング練習")}
              </button>
            )}
          </div>
        </div>
      </section>

      <div className="today-grid">
        <WordOfDay />

        <section className="panel streak-panel">
          <div className="panel-head">
            <h3 className="eyebrow">{t("这一周", "今週")}</h3>
            <span className={`streak ${streak ? "is-on" : ""}`}>
              <Flame size={16} /> {t(`连续 ${streak} 天`, `${streak}日連続`)}
            </span>
          </div>
          <div className="streak-body">
            <Ring value={goal ? doneToday / goal : 0} size={112} stroke={8} tone="terra">
              <b>{doneToday}</b>
              <small>{t("今日答题", "今日の解答数")}</small>
            </Ring>
            <ol className="week">
              {week.map((d) => (
                <li key={d.k} className={`${d.v ? "is-on" : ""} ${d.today ? "is-today" : ""}`} title={t(`${d.k}：${d.v} 题`, `${d.k}：${d.v}問`)}>
                  <span style={{ "--h": Math.min(1, d.v / 40) } as React.CSSProperties} />
                  <small>{d.label}</small>
                </li>
              ))}
            </ol>
          </div>
          <dl className="mini-stats">
            <div>
              <dt>{t("已点亮", "灯した星")}</dt>
              <dd>{learned.toLocaleString()}</dd>
            </div>
            <div>
              <dt>{t("已掌握", "習得済み")}</dt>
              <dd>{mastered.toLocaleString()}</dd>
            </div>
            <div>
              <dt>{t("全部词汇", "全単語数")}</dt>
              <dd>{atlas.count.toLocaleString()}</dd>
            </div>
          </dl>
        </section>

        <LevelPath />
        <GalaxyPanel learned={learned} total={atlas.count} />
        <Topics />
      </div>
    </div>
  );
}

function GalaxyPanel({ learned, total }: { learned: number; total: number }) {
  const { t } = useI18n();
  const today = useStore((s) => s.progress.days[dayKey()]);
  const ids = useStore((s) => s.progress.cards);
  const todayIds = useMemo(() => {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    return Object.entries(ids)
      .filter(([, c]) => c.seen >= start.getTime())
      .map(([id]) => id);
  }, [ids]);
  void today;
  return (
    <section className="galaxy-panel" onClick={() => go({ page: "atlas", view: "galaxy" })} role="link" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && go({ page: "atlas", view: "galaxy" })}>
      <Galaxy mode="mini" highlight={todayIds} />
      <div className="galaxy-panel-copy">
        <p className="eyebrow eyebrow-light">{t("你的词汇星图", "あなたの単語の星図")}</p>
        <h3>
          {t("已点亮", "灯した星")} <b>{learned.toLocaleString()}</b> {t("颗星", "個")}
        </h3>
        <p>{learned ? t(`还有 ${(total - learned).toLocaleString()} 颗在等你。金色是今天新点亮的。`, `あと${(total - learned).toLocaleString()}個の星が待っています。金色は今日灯した星です。`) : t(`${total.toLocaleString()} 个词是 ${total.toLocaleString()} 颗星。学会一个，就点亮一颗。`, `${total.toLocaleString()}語が、${total.toLocaleString()}個の星に。一語覚えるたびに、一つ灯ります。`)}</p>
        <span className="btn btn-glass">
          {t("进入星图", "星図を開く")} <ArrowRight size={18} />
        </span>
      </div>
    </section>
  );
}

function WordOfDay() {
  const { t } = useI18n();
  const atlas = useAtlas();
  const pick = useMemo(() => {
    const pool = atlas.words.filter((w) => w.cefr >= 2 && w.media & 1);
    const list = pool.length ? pool : atlas.words;
    return list[hashSeed(dayKey()) % list.length];
  }, [atlas]);
  const { entry } = useEntry(pick?.id);
  if (!pick) return null;
  return (
    <section className="panel wotd" onClick={() => openWord(pick.id)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && openWord(pick.id)} aria-label={t(`今日一词：${pick.word}`, `今日の一語：${pick.word}`)}>
      <Illustration src={atlas.img(pick)} word={pick.word} topic={pick.topic} className="wotd-art" />
      <div className="wotd-body">
        <h3 className="eyebrow">{t("今日一词", "今日の一語")}</h3>
        <p className="wotd-word" lang="en">
          {pick.word}
        </p>
        {entry && (
          <div onClick={(e) => e.stopPropagation()}>
            <Pronounce entry={entry} refw={pick} />
          </div>
        )}
        <p className="wotd-zh">{pick.zh}</p>
        {entry?.ex[0] && (
          <p className="wotd-ex" lang="en">
            <Highlight text={entry.ex[0].en} word={entry.w} />
          </p>
        )}
      </div>
    </section>
  );
}

function LevelPath() {
  const { t } = useI18n();
  const atlas = useAtlas();
  const cards = useStore((s) => s.progress.cards);
  const start = useStore((s) => s.settings.startLevel);
  const levels = useMemo(() => {
    const out = atlas.cefr.map((name) => ({ name, total: 0, seen: 0, mastered: 0 }));
    for (const w of atlas.words) {
      const l = out[w.cefr];
      l.total++;
      const c = cards[w.id];
      if (c) {
        l.seen++;
        if (isMastered(c)) l.mastered++;
      }
    }
    return out;
  }, [atlas, cards]);
  const NAMES = [t("入门", "入門"), t("基础", "基礎"), t("进阶", "中級"), t("中高", "中上級"), t("高级", "上級"), t("精通", "熟達")];
  return (
    <section className="panel path-panel">
      <div className="panel-head">
        <h3 className="eyebrow">{t("学习路线 · 从 A1 到 C2", "学習ルート · A1からC2へ")}</h3>
        <span className="legend">
          <i className="lg-seen" /> {t("已学", "学習済み")} <i className="lg-done" /> {t("已掌握", "習得済み")}
        </span>
      </div>
      <ol className="route">
        {levels.map((l, i) => {
          const seen = l.seen / Math.max(1, l.total);
          const done = l.mastered / Math.max(1, l.total);
          return (
            <li key={l.name} className={`${i === start ? "is-start" : ""} ${l.seen ? "is-on" : ""}`}>
              <button onClick={() => go({ page: "atlas", level: l.name })} aria-label={t(`${l.name} ${NAMES[i]}，已学 ${l.seen} / ${l.total}`, `${l.name} ${NAMES[i]}、学習済み ${l.seen} / ${l.total}`)}>
                <span className="station" style={{ "--seen": seen, "--done": done } as React.CSSProperties}>
                  <b>{l.name}</b>
                </span>
                <span className="station-name">{NAMES[i]}</span>
                <span className="station-count">
                  {l.seen}
                  <small>/{l.total}</small>
                </span>
                {i === start && <span className="station-flag">{t("起点", "スタート")}</span>}
              </button>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function Topics() {
  const { t } = useI18n();
  const atlas = useAtlas();
  const counts = useMemo(() => {
    const c = new Array(atlas.topics.length).fill(0);
    atlas.words.forEach((w) => c[w.topic]++);
    return c;
  }, [atlas]);
  return (
    <section className="topics-panel">
      <div className="panel-head">
        <h3 className="eyebrow">{t("按雅思话题探索", "IELTSのトピックから探す")}</h3>
        <button className="link" onClick={() => go({ page: "atlas" })}>
          {t("打开图鉴", "単語図鑑を開く")}
        </button>
      </div>
      <ul className="topic-tiles">
        {atlas.topics.map(([key, name], i) => (
          <li key={key}>
            <button onClick={() => go({ page: "atlas", topic: key })}>
              <img src={`${BRAND}/topic-${key}.webp`} alt="" loading="lazy" onError={(e) => (e.currentTarget.style.visibility = "hidden")} />
              <span>
                <b>{name}</b>
                <small>{t(`${counts[i]} 个词`, `${counts[i]}語`)}</small>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
