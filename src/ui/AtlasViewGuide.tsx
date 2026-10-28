import {
  cloneElement,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type HTMLAttributes,
  type ReactElement,
} from "react";
import { useI18n } from "../i18n";
import "./AtlasViewGuide.css";

const STORAGE_KEY = "word-atlas:guide:atlas-view:v1";
let dismissedThisSession = false;

function readDismissed() {
  if (dismissedThisSession) return true;
  try {
    return localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

export function AtlasViewGuide({
  enabled = true,
  children,
}: {
  enabled?: boolean;
  children: ReactElement<HTMLAttributes<HTMLElement>>;
}) {
  const { language, t } = useI18n();
  const id = useId();
  const target = useRef<HTMLDivElement>(null);
  const popover = useRef<HTMLDivElement>(null);
  const [dismissed, setDismissed] = useState(readDismissed);
  const [inView, setInView] = useState(false);
  const [position, setPosition] = useState({ left: 0, width: 260, arrow: 130, above: false });
  const open = enabled && inView && !dismissed;

  const dismiss = useCallback(() => {
    const restoreFocus = popover.current?.contains(document.activeElement);
    dismissedThisSession = true;
    setDismissed(true);
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // The in-memory flag also survives route changes when storage is blocked.
    }
    if (restoreFocus) {
      (target.current?.querySelector<HTMLButtonElement>('button[aria-pressed="true"]') ??
        target.current?.querySelector<HTMLButtonElement>("button"))?.focus();
    }
  }, []);

  useEffect(() => {
    if (!enabled || dismissed || !target.current) return;
    if (typeof IntersectionObserver === "undefined") {
      setInView(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting && entry.intersectionRatio >= 0.75),
      { threshold: [0, 0.75] },
    );
    observer.observe(target.current);
    return () => observer.disconnect();
  }, [enabled, dismissed]);

  const place = useCallback(() => {
    if (!target.current) return;
    const rect = target.current.getBoundingClientRect();
    const width = Math.min(260, window.innerWidth - 32);
    const left = Math.max(16, Math.min(rect.right - width, window.innerWidth - width - 16));
    const height = popover.current?.offsetHeight ?? 170;
    const next = {
      left: left - rect.left,
      width,
      arrow: Math.max(20, Math.min(width - 20, rect.left + rect.width / 2 - left)),
      above: window.innerHeight - rect.bottom < height + 20 && rect.top > height + 20,
    };
    setPosition((previous) =>
      previous.left === next.left && previous.width === next.width &&
      previous.arrow === next.arrow && previous.above === next.above ? previous : next,
    );
  }, []);

  useLayoutEffect(() => {
    if (!open) return;
    place();
    const escape = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || event.defaultPrevented) return;
      const modalOpen = Array.from(
        document.querySelectorAll('[role="dialog"][aria-modal="true"]'),
      ).some((dialog) => dialog.getClientRects().length > 0);
      if (!modalOpen) dismiss();
    };
    window.addEventListener("resize", place);
    window.addEventListener("scroll", place, { capture: true, passive: true });
    document.addEventListener("keydown", escape);
    return () => {
      window.removeEventListener("resize", place);
      window.removeEventListener("scroll", place, true);
      document.removeEventListener("keydown", escape);
    };
  }, [open, language, place, dismiss]);

  useEffect(() => {
    const sync = (event: StorageEvent) => {
      if (event.key === STORAGE_KEY && event.newValue === "1") {
        dismissedThisSession = true;
        setDismissed(true);
      }
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);

  return (
    <div className={`atlas-view-guide${open ? " is-open" : ""}`}>
      <div
        className="atlas-view-guide-target"
        ref={target}
        onClickCapture={(event) => {
          if (enabled && !dismissed && event.target instanceof Element && event.target.closest("button")) dismiss();
        }}
      >
        {cloneElement(children, {
          "aria-describedby": [children.props["aria-describedby"], open ? `${id}-description` : undefined]
            .filter(Boolean).join(" ") || undefined,
        })}
      </div>
      {open && (
        <div
          ref={popover}
          className={`atlas-view-guide-popover${position.above ? " is-above" : ""}`}
          style={{ left: position.left, width: position.width, "--guide-arrow": `${position.arrow}px` } as CSSProperties}
          role="note"
          aria-labelledby={`${id}-title`}
        >
          <p className="atlas-view-guide-title" id={`${id}-title`}>
            {t("换个看法", "表示を切り替えてみよう")}
          </p>
          <p className="atlas-view-guide-description" id={`${id}-description`}>
            {t("试试列表，或看看词汇星图。", "リストや単語の星図も見てみましょう。")}
          </p>
          <button type="button" className="atlas-view-guide-dismiss" onClick={dismiss}>
            {t("知道了", "わかりました")}
          </button>
        </div>
      )}
    </div>
  );
}
