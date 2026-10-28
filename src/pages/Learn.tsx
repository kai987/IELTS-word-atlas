import { useI18n } from "../i18n";
import { ArrowRight, Check, Lightbulb, RotateCcw, Share2, Volume2, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { prefetch, useAtlas, useEntry } from "../atlas/context";
import type { Entry, WordRef } from "../atlas/types";
import { play, stopAudio } from "../lib/audio";
import { burst } from "../lib/burst";
import { cue } from "../lib/sound";
import { go } from "../lib/router";
import { gap, normalize } from "../lib/text";
import { answer, advance, buildSession, gradeFor, sessionStats } from "../store/session";
import { Rating } from "../store/srs";
import { store, useStore, type ActiveSession, type QuizKind, type Step } from "../store/store";
import { EntryView, Highlight } from "../ui/EntryView";
import { Illustration } from "../ui/Illustration";
import { Galaxy } from "../galaxy/Galaxy";
import { AmbiencePicker } from "../ui/Ambience";
import { Ring } from "../ui/Ring";
import { Speak } from "../ui/Speak";
import { shareSession } from "../ui/shareSession";

export function Learn() {
  const atlas = useAtlas();
  const session = useStore((s) => s.progress.session);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const { progress, settings } = store.get();
    if (!progress.session) {
      const s = buildSession(atlas, progress, settings);
      if (!s.steps.length) {
        go({ page: "today" }, null, true);
        return;
      }
      store.progress((p) => ({ ...p, session: s }));
    }
  }, [atlas]);

  const ids = useMemo(() => [...new Set(session?.steps.map((s) => s.id) ?? [])], [session?.id]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!ids.length) return;
    let live = true;
    // Load the first chunk before rendering, the rest in the background.
    prefetch(atlas, ids.slice(0, 6)).then(() => live && setReady(true));
    void prefetch(atlas, ids);
    return () => {
      live = false;
    };
  }, [atlas, ids]);

  useEffect(() => () => stopAudio(), []);

  if (!session || !ready) return <div className="learn learn-loading"><span className="spinner" /></div>;
  if (session.finished || session.index >= session.steps.length) return <Summary session={session} />;
  return <Runner session={session} />;
}

function Runner({ session }: { session: ActiveSession }) {
  const { t } = useI18n();
  const step = session.steps[session.index];
  const total = session.steps.length;
  const exit = () => {
    stopAudio();
    go({ page: "today" });
  };
  return (
    <div className="learn">
      <header className="learn-top">
        <button className="icon-btn" onClick={exit} aria-label={t("暂停并返回", "中断して戻る")}>
          <X size={22} />
        </button>
        <div className="learn-progress" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={session.index}>
          <span style={{ width: `${(session.index / total) * 100}%` }} />
        </div>
        <span className="learn-count">
          {session.index + 1}
          <small>/{total}</small>
        </span>
        <AmbiencePicker />
      </header>
      <main className="learn-stage" key={`${session.id}-${session.index}`}>
        {step.kind === "intro" ? <Intro step={step} /> : <Quiz step={step as Step & { kind: QuizKind }} session={session} />}
      </main>
    </div>
  );
}

function useStepTimer() {
  const t = useRef(performance.now());
  return () => (performance.now() - t.current) / 1000;
}

function Intro({ step }: { step: Step }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const { entry } = useEntry(step.id);
  const settings = useStore((s) => s.settings);
  const elapsed = useStepTimer();
  useEffect(() => {
    if (entry && settings.autoplay) void play(atlas.audio(entry, settings.accent), entry.w, settings.accent);
  }, [entry, atlas, settings.autoplay, settings.accent]);
  const next = useCallback(() => {
    stopAudio();
    if (store.get().settings.sfx) void cue("flip");
    advance(elapsed());
  }, [elapsed]);
  useKeys({ Enter: next, " ": next });
  if (!entry) return <span className="spinner" />;
  return (
    <div className="intro">
      <p className="stage-label">
        <span className="dot dot-new" /> {t("初次见面", "はじめての単語")}
      </p>
      <EntryView entry={entry} mode="intro" />
      <footer className="learn-actions">
        <button className="btn btn-primary btn-xl" onClick={next} autoFocus>
          {t("认识了", "覚えた")} <ArrowRight size={20} />
        </button>
        <span className="hint-keys">
          <kbd>Enter</kbd> {t("继续", "続ける")}
        </span>
      </footer>
    </div>
  );
}


function Quiz({ step, session }: { step: Step & { kind: QuizKind }; session: ActiveSession }) {
  const { t, language } = useI18n();
  const KIND_LABEL: Record<QuizKind, string> = {
    meaning: t("它是什么意思？", "この単語の意味は？"),
    picture: t("看图，补全这句话", "絵を見て、文を完成させましょう"),
    listen: t("听，是哪个词？", "聞こえた単語は？"),
    spell: t("拼出这个词", "この単語のスペルを入力しましょう"),
  };
  const atlas = useAtlas();
  const ref = atlas.byId.get(step.id)!;
  const { entry } = useEntry(step.id);
  const settings = useStore((s) => s.settings);
  const pending = session.pending;
  const elapsed = useStepTimer();
  const [hints, setHints] = useState(0);
  const options = useMemo(() => (step.options ?? []).map((id) => atlas.byId.get(id)!).filter(Boolean), [atlas, step.options]);

  const submit = useCallback(
    (value: string, correct: boolean) => {
      if (pending) return;
      const ms = elapsed() * 1000;
      if (correct) {
        const el = document.querySelector<HTMLElement>(step.kind === "spell" ? ".slots" : `[data-option="${value}"]`);
        const r = el?.getBoundingClientRect();
        if (r) burst(r.left + r.width / 2, r.top + r.height / 2);
      }
      if (settings.sfx) void cue(correct ? "correct" : "wrong");
      answer(atlas, step, correct, gradeFor(step.kind, correct, ms, hints > 0), value);
      if (entry) void play(atlas.audio(entry, settings.accent), entry.w, settings.accent);
    },
    [pending, elapsed, settings, atlas, step, hints, entry],
  );

  const next = useCallback(() => {
    stopAudio();
    advance(elapsed());
  }, [elapsed]);

  useEffect(() => {
    if (step.kind === "listen" && entry && !pending) void play(atlas.audio(entry, settings.accent), entry.w, settings.accent);
  }, [step.kind, entry, atlas, settings.accent, pending]);

  const keys: Record<string, () => void> = {};
  if (pending) {
    keys.Enter = next;
    keys[" "] = next;
  } else if (step.kind !== "spell") {
    options.forEach((o, i) => (keys[String(i + 1)] = () => submit(o.id, o.id === ref.id)));
  }
  useKeys(keys);

  if (!entry) return <span className="spinner" />;
  const sentence = entry.ex[0] ? gap(entry.ex[0].en, entry.w) : null;

  return (
    <div className={`quiz quiz-${step.kind} ${pending ? (pending.correct ? "is-right" : "is-wrong") : ""}`}>
      <p className="stage-label">
        <span className={`dot ${step.retry ? "dot-retry" : "dot-review"}`} />
        {step.retry ? t("再见一面 · ", "もう一度 · ") : ""}
        {KIND_LABEL[step.kind]}
      </p>

      <section className="prompt">
        {step.kind === "meaning" && (
          <div className="prompt-word">
            <h2 className="headword" lang="en">
              {entry.w}
            </h2>
            <Speak url={atlas.audio(entry, settings.accent)} text={entry.w} accent={settings.accent} label={<span className="ipa">{settings.accent === "us" ? entry.us || entry.uk : entry.uk || entry.us}</span>} />
          </div>
        )}
        {step.kind === "picture" && (
          <div className="prompt-picture">
            <Illustration src={atlas.img(entry)} word={entry.w} topic={ref.topic} eager />
            <p className="cloze" lang="en">
              {sentence ? (
                <>
                  {sentence.before}
                  <span className="blank">{pending ? sentence.hidden : "　　　"}</span>
                  {sentence.after}
                </>
              ) : (
                entry.senses[0].zh
              )}
            </p>
            {sentence && pending && <p className="cloze-zh">{entry.ex[0].zh}</p>}
          </div>
        )}
        {step.kind === "listen" && (
          <div className="prompt-listen">
            <button className="listen-orb" onClick={() => play(atlas.audio(entry, settings.accent), entry.w, settings.accent)} aria-label={t("再听一遍", "もう一度聞く")}>
              <Volume2 size={40} strokeWidth={1.6} />
              <span />
            </button>
            <button className="link" onClick={() => play(atlas.audio(entry, settings.accent), entry.w, settings.accent, 0.7)}>
              {t("慢速再听", "ゆっくり聞く")}
            </button>
          </div>
        )}
        {step.kind === "spell" && <SpellPrompt entry={entry} refw={ref} hints={hints} />}
      </section>

      {step.kind === "spell" ? (
        <SpellInput entry={entry} pending={pending} hints={hints} onHint={() => setHints((h) => Math.min(entry.w.length - 1, h + 1))} onSubmit={(v) => submit(v, normalize(v) === normalize(entry.w))} />
      ) : (
        <ul className={`options ${step.kind === "meaning" ? "options-zh" : "options-en"}`}>
          {options.map((o, i) => {
            const isAnswer = o.id === ref.id;
            const chosen = pending?.value === o.id;
            const cls = pending ? (isAnswer ? "is-answer" : chosen ? "is-chosen" : "is-dim") : "";
            return (
              <li key={o.id}>
                <button className={`option ${cls}`} data-option={o.id} onClick={() => submit(o.id, isAnswer)} disabled={!!pending}>
                  <kbd>{i + 1}</kbd>
                  <span lang={step.kind === "meaning" ? (language === "ja" ? "ja" : "zh-CN") : "en"}>{step.kind === "meaning" ? o.zh : o.word}</span>
                  {pending && isAnswer && <Check size={20} className="option-mark" />}
                  {pending && chosen && !isAnswer && <X size={20} className="option-mark" />}
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {pending && <Feedback entry={entry} refw={ref} correct={pending.correct} onNext={next} />}
    </div>
  );
}

function SpellPrompt({ entry, refw, hints }: { entry: Entry; refw: WordRef; hints: number }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const accent = useStore((s) => s.settings.accent);
  const sentence = entry.ex[0] ? gap(entry.ex[0].en, entry.w) : null;
  void hints;
  return (
    <div className="prompt-spell">
      <Illustration src={atlas.img(entry)} word={entry.w} topic={refw.topic} eager className="spell-art" />
      <div>
        <p className="spell-zh">
          <span className="pos">{entry.senses[0].pos}</span> {entry.senses[0].zh}
        </p>
        {sentence && (
          <p className="cloze cloze-sm" lang="en">
            {sentence.before}
            <span className="blank">　　　</span>
            {sentence.after}
          </p>
        )}
        <Speak url={atlas.audio(entry, accent)} text={entry.w} accent={accent} size="sm" label={t("听发音", "発音を聞く")} />
      </div>
    </div>
  );
}

function SpellInput({ entry, pending, hints, onHint, onSubmit }: { entry: Entry; pending?: { correct: boolean; value: string }; hints: number; onHint: () => void; onSubmit: (v: string) => void }) {
  const { t } = useI18n();
  const [value, setValue] = useState("");
  const input = useRef<HTMLInputElement>(null);
  const target = entry.w;
  const prefix = target.slice(0, hints);
  useEffect(() => {
    if (hints && !normalize(value).startsWith(normalize(prefix))) setValue(prefix);
    input.current?.focus();
  }, [hints]); // eslint-disable-line react-hooks/exhaustive-deps
  const shown = pending ? pending.value : value;
  return (
    <form
      className="spell"
      onSubmit={(e) => {
        e.preventDefault();
        if (!pending && value.trim()) onSubmit(value);
      }}
    >
      <div className="slots" aria-hidden="true" onClick={() => input.current?.focus()}>
        {Array.from(target).map((ch, i) => {
          const typed = shown[i];
          const ok = typed !== undefined && typed.toLowerCase() === ch.toLowerCase();
          return (
            <span key={i} className={`slot ${ch === " " ? "slot-space" : ""} ${typed !== undefined ? (pending ? (ok ? "is-ok" : "is-bad") : "is-filled") : ""} ${!pending && i === shown.length ? "is-caret" : ""}`}>
              {pending && !pending.correct ? ch : typed ?? ""}
            </span>
          );
        })}
      </div>
      <input
        ref={input}
        className="spell-input"
        value={shown}
        onChange={(e) => !pending && setValue(e.target.value.slice(0, target.length + 6))}
        autoFocus
        autoCapitalize="off"
        autoCorrect="off"
        autoComplete="off"
        spellCheck={false}
        enterKeyHint="done"
        aria-label={t(`拼写，${target.length} 个字符`, `スペル入力、${target.length}文字`)}
        readOnly={!!pending}
      />
      {!pending && (
        <div className="spell-actions">
          <button type="button" className="btn btn-ghost" onClick={onHint} disabled={hints >= target.length - 1}>
            <Lightbulb size={17} /> {t("提示字母", "文字のヒント")}
          </button>
          <button type="submit" className="btn btn-primary" disabled={!value.trim()}>
            {t("确认", "確定")} <kbd>Enter</kbd>
          </button>
        </div>
      )}
    </form>
  );
}

function Feedback({ entry, refw, correct, onNext }: { entry: Entry; refw: WordRef; correct: boolean; onNext: () => void }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const btn = useRef<HTMLButtonElement>(null);
  useEffect(() => btn.current?.focus({ preventScroll: true }), []);
  return (
    <div className={`feedback ${correct ? "is-right" : "is-wrong"}`} role="status">
      <div className="feedback-inner">
        <Illustration src={atlas.img(entry, "thumb")} word={entry.w} topic={refw.topic} className="feedback-art" />
        <div className="feedback-text">
          <p className="feedback-verdict">{correct ? t("答对了", "正解です") : t("没关系，记住它", "大丈夫、ここで覚えましょう")}</p>
          <p className="feedback-word">
            <b lang="en">{entry.w}</b>
            <span className="ipa">{entry.uk || entry.us}</span>
          </p>
          <p className="feedback-zh">
            {entry.senses
              .slice(0, 2)
              .map((s) => `${s.pos} ${s.zh}`)
              .join("　")}
          </p>
          {entry.ex[0] && (
            <p className="feedback-ex" lang="en">
              <Highlight text={entry.ex[0].en} word={entry.w} />
            </p>
          )}
        </div>
        <button ref={btn} className={`btn btn-xl ${correct ? "btn-sage" : "btn-terra"}`} onClick={onNext}>
          {t("继续", "続ける")} <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
}

function Summary({ session }: { session: ActiveSession }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  useEffect(() => {
    if (store.get().settings.sfx) void cue("complete");
  }, []);
  const stats = sessionStats(session);
  const words = [...new Set(session.steps.map((s) => s.id))].map((id) => atlas.byId.get(id)!).filter(Boolean);
  const wrong = words.filter((w) => session.graded[w.id] === Rating.Again);
  const minutes = Math.max(1, Math.round(((session.finished ?? Date.now()) - session.started) / 60000));
  const done = () => {
    store.progress((p) => ({ ...p, session: null }));
    go({ page: "today" });
  };
  const again = () => {
    const { progress, settings } = store.get();
    store.progress((p) => ({ ...p, session: buildSession(atlas, progress, settings, { ids: wrong.map((w) => w.id) }) }));
  };
  return (
    <div className="learn summary">
      <div className="summary-card">
        <div className="summary-sky">
          <Galaxy mode="mini" highlight={words.map((w) => w.id)} ignite />
          <p>{t(`今天点亮了 ${words.length} 颗星`, `今日は${words.length}個の星を灯しました`)}</p>
        </div>
        <p className="eyebrow">{t("这一程结束了", "今回の学習が終わりました")}</p>
        <h1 className="display">{stats.accuracy >= 90 ? t("漂亮的一程。", "すばらしい学習でした。") : stats.accuracy >= 60 ? t("稳稳向前。", "着実に前へ。") : t("错过的，会再相遇。", "間違えた単語には、また出会えます。")}</h1>
        <div className="summary-stats">
          <Ring value={stats.accuracy / 100} size={128} tone={stats.accuracy >= 60 ? "sage" : "terra"}>
            <b>{stats.accuracy}%</b>
            <small>{t("首次正确", "初回正答率")}</small>
          </Ring>
          <dl>
            <div>
              <dt>{t("新词", "新しい単語")}</dt>
              <dd>{session.newIds.length}</dd>
            </div>
            <div>
              <dt>{t("复习", "復習")}</dt>
              <dd>{session.reviewIds.length}</dd>
            </div>
            <div>
              <dt>{t("用时", "所要時間")}</dt>
              <dd>
                {minutes}
                <small>{t("分钟", "分")}</small>
              </dd>
            </div>
          </dl>
        </div>
        <ul className="summary-words">
          {words.map((w) => (
            <li key={w.id} className={session.graded[w.id] === Rating.Again ? "is-wrong" : ""}>
              <Illustration src={atlas.img(w, "thumb")} word={w.word} topic={w.topic} />
              <span lang="en">{w.word}</span>
              <small>{w.zh}</small>
            </li>
          ))}
        </ul>
        <p className="summary-note">{t("FSRS 已为每个词排好下次相遇的时间。答错的词，会更早回来。", "FSRSが各単語の次の復習時期を設定しました。間違えた単語は、早めにもう一度登場します。")}</p>
        <div className="summary-actions">
          {wrong.length > 0 && (
            <button className="btn btn-ghost" onClick={again}>
              <RotateCcw size={18} /> {t(`再练 ${wrong.length} 个错词`, `間違えた${wrong.length}語を復習`)}
            </button>
          )}
          <button className="btn btn-ghost" onClick={() => shareSession(atlas, session)}>
            <Share2 size={18} /> {t("分享成绩卡", "学習結果をシェア")}
          </button>
          <button className="btn btn-primary btn-xl" onClick={done} ref={(b) => b?.focus({ preventScroll: true })}>
            {t("完成", "完了")} <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

/** Page-level shortcuts that ignore typing in inputs (except Enter, which forms handle). */
export function useKeys(map: Record<string, () => void>) {
  const ref = useRef(map);
  ref.current = map;
  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey || e.repeat) return;
      const t = e.target as HTMLElement;
      const typing = t.tagName === "INPUT" || t.tagName === "TEXTAREA";
      if (typing && !(e.key === "Enter" && (t as HTMLInputElement).readOnly)) return;
      if (t.tagName === "BUTTON" && (e.key === "Enter" || e.key === " ")) return;
      const fn = ref.current[e.key];
      if (fn) {
        e.preventDefault();
        fn();
      }
    };
    window.addEventListener("keydown", on);
    return () => window.removeEventListener("keydown", on);
  }, []);
}
