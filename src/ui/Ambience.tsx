import { useI18n } from "../i18n";
import { AudioLines, Check, CloudRain, Coffee, Flame, Sailboat, Sparkles, Trees, VolumeX, Waves } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { AMBIENCE, primeCues, setAmbience, type AmbienceId } from "../lib/sound";
import { store, useStore } from "../store/store";

const ICONS: Record<AmbienceId, typeof CloudRain> = { stars: Sparkles, rain: CloudRain, sea: Waves, forest: Trees, fire: Flame, voyage: Sailboat, cafe: Coffee };

/** Keeps the ambience in sync with settings; browsers only allow audio after a user gesture. */
export function AmbienceController() {
  const ambience = useStore((s) => s.settings.ambience);
  const volume = useStore((s) => s.settings.ambienceVolume);
  const [armed, setArmed] = useState(false);
  useEffect(() => {
    const arm = () => {
      primeCues();
      setArmed(true);
    };
    window.addEventListener("pointerdown", arm, { once: true });
    window.addEventListener("keydown", arm, { once: true });
    return () => {
      window.removeEventListener("pointerdown", arm);
      window.removeEventListener("keydown", arm);
    };
  }, []);
  useEffect(() => {
    if (armed) void setAmbience(ambience === "off" ? null : ambience, volume);
  }, [armed, ambience, volume]);
  return null;
}

export function AmbiencePicker() {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const ambience = useStore((s) => s.settings.ambience);
  const volume = useStore((s) => s.settings.ambienceVolume);
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const close = (e: Event) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !box.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("pointerdown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);
  const on = ambience !== "off";
  return (
    <div className="amb" ref={box}>
      <button className={`icon-btn amb-btn ${on ? "is-on" : ""}`} onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-label={t("环境声", "環境音")} title={t("环境声", "環境音")}>
        <AudioLines size={19} />
        {on && <span className="amb-bars" aria-hidden="true"><i /><i /><i /></span>}
      </button>
      {open && (
        <div className="amb-pop" role="dialog" aria-label={t("环境声", "環境音")}>
          <p className="eyebrow">{t("环境声 · 专注陪伴", "環境音 · 集中のおともに")}</p>
          <ul>
            {AMBIENCE.map(({ id, label }) => {
              const Icon = ICONS[id];
              const sel = ambience === id;
              return (
                <li key={id}>
                  <button className={sel ? "is-on" : ""} onClick={() => store.settings({ ambience: sel ? "off" : id })} aria-pressed={sel}>
                    <Icon size={18} strokeWidth={1.7} />
                    <span>{t(label, ({ stars: "星空の音楽", rain: "雨の日の図書館", sea: "早朝の海辺", forest: "朝の森", fire: "夜の暖炉", voyage: "航海中の船室", cafe: "静かなカフェ" } as const)[id])}</span>
                    {sel && <Check size={16} />}
                  </button>
                </li>
              );
            })}
            <li>
              <button className={!on ? "is-on" : ""} onClick={() => store.settings({ ambience: "off" })} aria-pressed={!on}>
                <VolumeX size={18} strokeWidth={1.7} />
                <span>{t("安静", "オフ")}</span>
                {!on && <Check size={16} />}
              </button>
            </li>
          </ul>
          <label className="amb-vol">
            <span>{t("音量", "音量")}</span>
            <input type="range" min={0} max={1} step={0.05} value={volume} onChange={(e) => store.settings({ ambienceVolume: Number(e.target.value) })} disabled={!on} />
          </label>
          <p className="amb-note">{t("读单词时会自动压低环境声。", "単語の読み上げ中は環境音の音量が自動で下がります。")}</p>
        </div>
      )}
    </div>
  );
}
