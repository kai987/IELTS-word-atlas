import { useI18n } from "../i18n";
import { Download, RotateCcw, Upload } from "lucide-react";
import { useMemo, useRef } from "react";
import { useAtlas } from "../atlas/context";
import { isMastered } from "../store/srs";
import { dayKey, exportBackup, importBackup, resetProgress, store, useStore, type Settings } from "../store/store";
import { toast } from "../ui/Toast";
import { streakOf } from "./Today";

export function Me({ privateAvailable }: { privateAvailable: boolean }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const progress = useStore((s) => s.progress);
  const settings = useStore((s) => s.settings);
  const saveError = useStore((s) => s.saveError);
  const file = useRef<HTMLInputElement>(null);

  const stats = useMemo(() => {
    const cards = Object.values(progress.cards);
    const days = Object.values(progress.days);
    const r = days.reduce((n, d) => n + d.r, 0);
    const c = days.reduce((n, d) => n + d.c, 0);
    const t = days.reduce((n, d) => n + d.t, 0);
    const now = Date.now();
    const forecast = Array.from({ length: 7 }, (_, i) => {
      const end = new Date();
      end.setHours(23, 59, 59, 999);
      end.setDate(end.getDate() + i);
      const start = new Date(end);
      start.setHours(0, 0, 0, 0);
      return cards.filter((x) => (i === 0 ? x.due <= end.getTime() : x.due >= start.getTime() && x.due <= end.getTime())).length;
    });
    void now;
    return { learned: cards.length, mastered: cards.filter(isMastered).length, reviews: r, accuracy: r ? Math.round((c / r) * 100) : 0, minutes: Math.round(t / 60), forecast };
  }, [progress]);

  const set = (patch: Partial<Settings>) => store.settings(patch);
  const download = () => {
    const blob = new Blob([exportBackup()], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `word-atlas-backup-${dayKey()}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };
  const restore = async (f: File) => {
    if (f.size > 30 * 1024 * 1024) return toast(t("文件太大，不像是学习备份。", "ファイルが大きすぎます。学習データのバックアップか確認してください。"), "warn");
    const r = importBackup(await f.text());
    toast(r.ok ? t(`已恢复 ${r.cards} 个词的记忆`, `${r.cards}語の学習記録を復元しました`) : r.error, r.ok ? "ok" : "warn");
  };
  const maxF = Math.max(1, ...stats.forecast);

  return (
    <div className="page me">
      <header className="page-head">
        <p className="eyebrow">{t("我的", "マイページ")}</p>
        <h1 className="display">{t("你的星空", "あなたの星空")}</h1>
      </header>

      <section className="stat-strip">
        <div>
          <dt>{t("连续学习", "連続学習")}</dt>
          <dd>
            {streakOf(progress.days)}
            <small>{t("天", "日")}</small>
          </dd>
        </div>
        <div>
          <dt>{t("已点亮", "灯した星")}</dt>
          <dd>{stats.learned.toLocaleString()}</dd>
        </div>
        <div>
          <dt>{t("长期记住", "長期記憶")}</dt>
          <dd>{stats.mastered.toLocaleString()}</dd>
        </div>
        <div>
          <dt>{t("首次正确率", "初回正答率")}</dt>
          <dd>
            {stats.accuracy}
            <small>%</small>
          </dd>
        </div>
        <div>
          <dt>{t("学习时长", "学習時間")}</dt>
          <dd>
            {stats.minutes}
            <small>{t("分钟", "分")}</small>
          </dd>
        </div>
      </section>

      <div className="me-grid">
        <section className="panel">
          <h3 className="eyebrow">{t("过去 20 周", "過去20週間")}</h3>
          <Heatmap days={progress.days} />
          <p className="muted">{t("一格是一天，颜色越深，那天答得越多。「长期记住」指记忆稳定度超过 21 天。", "1マスが1日です。色が濃いほど、その日に解いた問題が多いことを表します。「長期記憶」は記憶の安定度が21日を超えた単語です。")}</p>
        </section>

        <section className="panel">
          <h3 className="eyebrow">{t("未来 7 天的复习量", "今後7日間の復習予定")}</h3>
          <ol className="forecast">
            {stats.forecast.map((n, i) => (
              <li key={i}>
                <span style={{ height: `${(n / maxF) * 100}%` }} />
                <b>{n}</b>
                <small>{i === 0 ? t("今天", "今日") : i === 1 ? t("明天", "明日") : `+${i}`}</small>
              </li>
            ))}
          </ol>
        </section>

        <section className="panel settings">
          <h3 className="eyebrow">{t("学习设置", "学習設定")}</h3>
          <Field label={t("每日新词", "1日の新しい単語数")} hint={t("复习不设上限，算法只安排快要遗忘的词。", "復習数に上限はありません。忘れかけている単語をアルゴリズムが選びます。")}>
            <div className="segmented">
              {[5, 10, 15, 20, 30].map((n) => (
                <button key={n} className={settings.dailyNew === n ? "is-on" : ""} onClick={() => set({ dailyNew: n })}>
                  {n}
                </button>
              ))}
            </div>
          </Field>
          <Field label={t("从哪个难度开始", "開始レベル")} hint={t("跳过已经熟悉的低级别词。", "すでに覚えている初級の単語をスキップできます。")}>
            <div className="segmented">
              {atlas.cefr.map((l, i) => (
                <button key={l} className={settings.startLevel === i ? "is-on" : ""} onClick={() => set({ startLevel: i })}>
                  {l}
                </button>
              ))}
            </div>
          </Field>
          <Field label={t("目标记忆率", "目標記憶保持率")} hint={t("越高复习越频繁。90% 是大多数人的甜点。", "高くするほど復習が増えます。多くの方には90%がおすすめです。")}>
            <div className="segmented">
              {[0.85, 0.9, 0.95].map((n) => (
                <button key={n} className={settings.retention === n ? "is-on" : ""} onClick={() => set({ retention: n })}>
                  {Math.round(n * 100)}%
                </button>
              ))}
            </div>
          </Field>
          <Field label={t("发音", "発音")}>
            <div className="segmented">
              <button className={settings.accent === "uk" ? "is-on" : ""} onClick={() => set({ accent: "uk" })}>
                {t("英式", "イギリス英語")}
              </button>
              <button className={settings.accent === "us" ? "is-on" : ""} onClick={() => set({ accent: "us" })}>
                {t("美式", "アメリカ英語")}
              </button>
            </div>
          </Field>
          <Field label={t("外观", "表示")}>
            <div className="segmented">
              {(
                [
                  ["system", t("跟随系统", "システム設定")],
                  ["light", t("浅色", "ライト")],
                  ["dark", t("深色", "ダーク")],
                ] as const
              ).map(([k, l]) => (
                <button key={k} className={settings.theme === k ? "is-on" : ""} onClick={() => set({ theme: k })}>
                  {l}
                </button>
              ))}
            </div>
          </Field>
          <Toggle label={t("自动播放发音", "発音を自動再生")} on={settings.autoplay} set={(v) => set({ autoplay: v })} />
          <Toggle label={t("界面音效", "操作音")} on={settings.sfx} set={(v) => set({ sfx: v })} />
          <Toggle label={t("开屏动画（每天一次）", "起動アニメーション（1日1回）")} on={settings.splash} set={(v) => set({ splash: v })} />
          <Toggle label={t("复习时加入拼写题", "復習にスペル問題を含める")} on={settings.spell} set={(v) => set({ spell: v })} />
          {privateAvailable && (
            <Field label={t("词库", "単語データ")} hint={t("私人词库只在本机开发服务器中可用，不会被打包发布。", "個人用の単語データはローカル開発サーバーでのみ利用でき、公開ビルドには含まれません。")}>
              <div className="segmented">
                <button className={settings.dataset === "open" ? "is-on" : ""} onClick={() => set({ dataset: "open" })}>
                  {t("开放图鉴", "公開単語図鑑")}
                </button>
                <button className={settings.dataset === "private" ? "is-on" : ""} onClick={() => set({ dataset: "private" })}>
                  {t("私人 8000", "個人用8000語")}
                </button>
              </div>
            </Field>
          )}
        </section>

        <section className="panel">
          <h3 className="eyebrow">{t("数据", "データ")}</h3>
          <p className="muted">{t("进度只存在这台设备的浏览器里：没有账号，没有服务器。换设备时，导出备份再导入即可。", "学習状況はこの端末のブラウザーに保存されます。アカウントもサーバーも不要です。端末を変えるときは、バックアップをエクスポートして新しい端末でインポートしてください。")}</p>
          {saveError && <p className="warn-text">{t("浏览器拒绝保存（可能是隐私模式或空间已满）。请尽快导出备份。", "ブラウザーに保存できませんでした（プライベートモードや空き容量不足の可能性があります）。早めにバックアップをエクスポートしてください。")}</p>}
          <div className="data-actions">
            <button className="btn btn-ghost" onClick={download}>
              <Download size={18} /> {t("导出备份", "バックアップをエクスポート")}
            </button>
            <button className="btn btn-ghost" onClick={() => file.current?.click()}>
              <Upload size={18} /> {t("导入备份", "バックアップをインポート")}
            </button>
            <input ref={file} type="file" accept="application/json,.json" hidden onChange={(e) => e.target.files?.[0] && restore(e.target.files[0]).finally(() => (e.target.value = ""))} />
            <button
              className="btn btn-ghost btn-danger"
              onClick={() => {
                if (confirm(t("确定清空这个词库的全部学习记录？此操作无法撤销，建议先导出备份。", "この単語データの学習記録をすべて削除しますか？この操作は取り消せません。先にバックアップをエクスポートすることをおすすめします。"))) {
                  resetProgress();
                  toast(t("学习记录已清空", "学習記録を削除しました"));
                }
              }}
            >
              <RotateCcw size={18} /> {t("清空记录", "学習記録を削除")}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <div>
        <b>{label}</b>
        {hint && <small>{hint}</small>}
      </div>
      {children}
    </div>
  );
}

function Toggle({ label, on, set }: { label: string; on: boolean; set: (v: boolean) => void }) {
  return (
    <label className="field toggle">
      <b>{label}</b>
      <input type="checkbox" role="switch" checked={on} onChange={(e) => set(e.target.checked)} />
      <span className="switch" aria-hidden="true" />
    </label>
  );
}

function Heatmap({ days }: { days: Record<string, { r: number }> }) {
  const { t } = useI18n();
  const weeks = 20;
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - (weeks * 7 - 1) - end.getDay());
  const cells: { k: string; v: number; future: boolean }[] = [];
  const d = new Date(start);
  for (let i = 0; i < (weeks + 1) * 7; i++) {
    const k = dayKey(d);
    cells.push({ k, v: days[k]?.r ?? 0, future: d > end });
    d.setDate(d.getDate() + 1);
  }
  const lvl = (v: number) => (v === 0 ? 0 : v < 10 ? 1 : v < 25 ? 2 : v < 50 ? 3 : 4);
  return (
    <div className="heatmap" role="img" aria-label={t("学习热力图", "学習ヒートマップ")}>
      {cells.map((c) => (
        <span key={c.k} className={`h${c.future ? "x" : lvl(c.v)}`} title={t(`${c.k} · ${c.v} 题`, `${c.k} · ${c.v}問`)} />
      ))}
    </div>
  );
}
