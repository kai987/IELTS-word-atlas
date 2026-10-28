import { useI18n } from "../i18n";
import { ArrowRight } from "lucide-react";
import { useState } from "react";
import { useAtlas } from "../atlas/context";
import { store } from "../store/store";


export function Onboarding() {
  const { t } = useI18n();
  const LEVELS = [
    ["A2", t("基础", "基礎"), t("日常词还不太稳", "日常の単語にまだ不安がある")],
    ["B1", t("进阶", "中級"), t("目标 5.5 – 6 分", "目標スコア 5.5〜6.0")],
    ["B2", t("中高", "中上級"), t("目标 6.5 – 7 分", "目標スコア 6.5〜7.0")],
    ["C1", t("高级", "上級"), t("冲刺 7.5 分以上", "7.5以上を目指す")],
  ];
  const atlas = useAtlas();
  const [level, setLevel] = useState(1);
  const [goal, setGoal] = useState(10);
  const finish = () => store.settings({ onboarded: true, startLevel: atlas.cefr.indexOf(LEVELS[level][0]), dailyNew: goal });
  return (
    <div className="onboard" role="dialog" aria-modal="true" aria-label={t("欢迎", "ようこそ")}>
      <div className="onboard-card">
        <img className="onboard-art" src={`${import.meta.env.BASE_URL}brand/hero.webp`} alt="" />
        <div className="onboard-body">
          <p className="eyebrow">{t("欢迎来到词光", "詞光へようこそ")}</p>
          <h1 className="display">
            {t(`${atlas.count.toLocaleString()} 颗星，`, `${atlas.count.toLocaleString()}個の星を、`)}
            <br />
            {t("等你一颗颗点亮。", "一つずつ灯していこう。")}
          </h1>
          <fieldset>
            <legend>{t("你从哪里出发？", "どのレベルから始めますか？")}</legend>
            <div className="choice-grid">
              {LEVELS.map(([code, name, desc], i) => (
                <button key={code} className={`choice ${level === i ? "is-on" : ""}`} onClick={() => setLevel(i)} aria-pressed={level === i}>
                  <span className={`chip chip-level lv-${code}`}>{code}</span>
                  <b>{name}</b>
                  <small>{desc}</small>
                </button>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend>{t("每天点亮几颗新星？", "1日に新しい星をいくつ灯しますか？")}</legend>
            <div className="segmented segmented-wide">
              {[5, 10, 15, 20].map((n) => (
                <button key={n} className={goal === n ? "is-on" : ""} onClick={() => setGoal(n)} aria-pressed={goal === n}>
                  {t(`${n} 颗`, `${n}個`)}{n === 10 ? t(" · 推荐", " · おすすめ") : ""}
                </button>
              ))}
            </div>
          </fieldset>
          <button className="btn btn-primary btn-xl" onClick={finish}>
            {t("出发", "始める")} <ArrowRight size={20} />
          </button>
          <p className="muted">{t("不用注册。进度只留在这台设备上，随时可以在「我的」里修改。", "登録は不要です。学習状況はこの端末に保存され、設定は「マイページ」でいつでも変更できます。")}</p>
        </div>
      </div>
    </div>
  );
}
