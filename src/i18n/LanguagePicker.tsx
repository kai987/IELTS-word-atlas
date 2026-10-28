import { useEffect, useId, useRef, useState } from "react";
import { setLanguage, useI18n, type Language } from ".";

const LANGUAGES: { id: Language; short: string; name: string; lang: string }[] =
  [
    { id: "zh", short: "中", name: "中文", lang: "zh-CN" },
    { id: "ja", short: "日", name: "日本語", lang: "ja" },
  ];

export function LanguagePicker() {
  const { language, t } = useI18n();
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const options = useRef<(HTMLButtonElement | null)[]>([]);
  const id = useId();

  useEffect(() => {
    if (!open) return;
    options.current[
      LANGUAGES.findIndex((item) => item.id === language)
    ]?.focus();
    const dismiss = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
        trigger.current?.focus();
      }
    };
    document.addEventListener("pointerdown", dismiss);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("pointerdown", dismiss);
      document.removeEventListener("keydown", escape);
    };
  }, [open, language]);

  return (
    <div
      className="language-picker"
      ref={root}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null))
          setOpen(false);
      }}
    >
      <button
        ref={trigger}
        className={`icon-btn language-trigger ${open ? "is-on" : ""}`}
        type="button"
        aria-label={t("选择语言", "言語を選択")}
        title={t("选择语言", "言語を選択")}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? id : undefined}
        onClick={() => setOpen((value) => !value)}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            setOpen(true);
          }
        }}
      >
        {language === "zh" ? "中" : "日"}
      </button>
      {open && (
        <div
          className="language-menu"
          id={id}
          role="menu"
          aria-label={t("语言", "言語")}
          onKeyDown={(event) => {
            const index = options.current.indexOf(
              document.activeElement as HTMLButtonElement,
            );
            const last = LANGUAGES.length - 1;
            const next =
              event.key === "ArrowDown"
                ? (index + 1) % LANGUAGES.length
                : event.key === "ArrowUp"
                  ? (index + last) % LANGUAGES.length
                  : event.key === "Home"
                    ? 0
                    : event.key === "End"
                      ? last
                      : -1;
            if (next >= 0) {
              event.preventDefault();
              options.current[next]?.focus();
            }
          }}
        >
          {LANGUAGES.map((item, index) => (
            <button
              key={item.id}
              type="button"
              role="menuitemradio"
              ref={(element) => {
                options.current[index] = element;
              }}
              lang={item.lang}
              className={language === item.id ? "is-selected" : ""}
              aria-checked={language === item.id}
              onClick={() => {
                setLanguage(item.id);
                setOpen(false);
                trigger.current?.focus();
              }}
            >
              <span className="language-initial">{item.short}</span>
              <span>{item.name}</span>
              <span className="language-check" aria-hidden="true">
                {language === item.id ? "✓" : ""}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
