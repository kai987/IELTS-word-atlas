import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Compass,
  Github,
  Keyboard,
  Moon,
  Search,
  Sun,
  User,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { AtlasContext, useAtlas, useEntry } from "./atlas/context";
import { loadOpenAtlas, loadPrivateAtlas } from "./atlas/data";
import { loadJapaneseAtlas } from "./atlas/japanese";
import { useI18n } from "./i18n";
import { LanguagePicker } from "./i18n/LanguagePicker";
import type { Atlas } from "./atlas/types";
import { REPO_URL } from "./config";
import {
  closeWord,
  currentLocation,
  go,
  openWord,
  useLocation,
  type Route,
} from "./lib/router";
import { AtlasPage } from "./pages/Atlas";
import { About } from "./pages/About";
import { Learn } from "./pages/Learn";
import { Me } from "./pages/Me";
import { Onboarding } from "./pages/Onboarding";
import { Practice } from "./pages/Practice";
import { Today } from "./pages/Today";
import { cue } from "./lib/sound";
import { store, useStore } from "./store/store";
import { EntryView } from "./ui/EntryView";
import { AmbienceController, AmbiencePicker } from "./ui/Ambience";
import { Logo } from "./ui/Logo";
import { Palette } from "./ui/Palette";
import { Sheet } from "./ui/Sheet";
import { shouldShowSplash, Splash } from "./ui/Splash";
import { Toasts } from "./ui/Toast";

const NAV: { page: Route["page"]; label: string; icon: typeof Compass }[] = [
  { page: "today", label: "今日", icon: Compass },
  { page: "atlas", label: "图鉴", icon: BookOpen },
  { page: "practice", label: "练习", icon: Keyboard },
  { page: "me", label: "我的", icon: User },
];

function useTheme() {
  const theme = useStore((s) => s.settings.theme);
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
    const dark =
      theme === "dark" ||
      (theme === "system" &&
        matchMedia("(prefers-color-scheme: dark)").matches);
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", dark ? "#0D1120" : "#F6F1E7");
  }, [theme]);
  return theme;
}

export default function App() {
  const { language, t } = useI18n();
  const [localized, setLocalized] = useState<{
    source: Atlas;
    atlas: Atlas;
  } | null>(null);
  const [localeError, setLocaleError] = useState<string | null>(null);
  const [localeAttempt, setLocaleAttempt] = useState(0);
  const [atlas, setAtlas] = useState<Atlas | null>(null);
  const [open, setOpen] = useState<Atlas | null>(null);
  const [priv, setPriv] = useState<Atlas | null>(null);
  const [error, setError] = useState<string | null>(null);
  const dataset = useStore((s) => s.settings.dataset);
  useTheme();

  useEffect(() => {
    loadOpenAtlas().then(
      (a) => {
        setOpen(a);
        if (import.meta.env.DEV) loadPrivateAtlas(a).then(setPriv, () => null);
      },
      (e: Error) => setError(e.message),
    );
  }, []);

  useEffect(() => {
    const next = dataset === "private" && priv ? priv : open;
    if (next && next !== atlas) {
      if (store.get().progress.datasetId !== next.id || !atlas)
        store.useDataset(next.id);
      setAtlas(next);
    }
  }, [dataset, open, priv, atlas]);

  useEffect(() => {
    document.documentElement.lang = language === "ja" ? "ja" : "zh-CN";
    const title = t(
      "词光 Word Atlas · 一词一画，点亮雅思",
      "詞光 Word Atlas · 一語に一枚の絵、IELTSを照らす",
    );
    const description = t(
      "7,298 个雅思核心词，每个词一幅原创插画、两句原创例句和英美发音。学会一个，就点亮一颗星。免费、开源、无需注册。",
      "IELTSの重要単語7,298語を、オリジナルのイラスト・例文2つ・英米の発音で学習。一語覚えるたびに、星が一つ輝きます。無料・オープンソース・登録不要。",
    );
    document.title = title;
    document
      .querySelector('link[rel="manifest"]')
      ?.setAttribute(
        "href",
        `${import.meta.env.BASE_URL}${language === "ja" ? "manifest.ja.webmanifest" : "manifest.webmanifest"}`,
      );
    for (const selector of [
      'meta[name="description"]',
      'meta[property="og:description"]',
    ])
      document.querySelector(selector)?.setAttribute("content", description);
    for (const selector of [
      'meta[name="twitter:title"]',
      'meta[property="og:title"]',
    ])
      document.querySelector(selector)?.setAttribute("content", title);
  }, [language, t]);

  useEffect(() => {
    setLocaleError(null);
    if (!atlas || language !== "ja") return;
    let live = true;
    loadJapaneseAtlas(atlas).then(
      (translated) => {
        if (live) setLocalized({ source: atlas, atlas: translated });
      },
      (error: Error) => {
        if (live) setLocaleError(error.message);
      },
    );
    return () => {
      live = false;
    };
  }, [atlas, language, localeAttempt]);

  const displayed =
    language === "ja"
      ? localized?.source === atlas
        ? localized.atlas
        : null
      : atlas;
  useEffect(() => {
    if (!atlas || (displayed && !localeError)) return;
    const blockHiddenShortcuts = (event: KeyboardEvent) => {
      if (!(event.target instanceof Element) || !event.target.closest(".boot"))
        event.stopImmediatePropagation();
    };
    window.addEventListener("keydown", blockHiddenShortcuts, true);
    return () =>
      window.removeEventListener("keydown", blockHiddenShortcuts, true);
  }, [atlas, displayed, localeError]);
  if (error)
    return (
      <div className="boot">
        <Logo />
        <p>{error}</p>
        <LanguagePicker />
        <button className="btn btn-primary" onClick={() => location.reload()}>
          {t("重新加载", "再読み込み")}
        </button>
      </div>
    );
  if (!atlas)
    return (
      <div className="boot" aria-busy="true">
        <Logo />
        <span className="spinner" />
        <p>{t("正在加载词库…", "単語データを読み込み中…")}</p>
      </div>
    );
  return (
    <AtlasContext.Provider value={displayed ?? atlas}>
      <div hidden={!displayed || !!localeError}>
        <Shell privateAvailable={!!priv} />
      </div>
      {(!displayed || localeError) && (
        <div
          className="boot"
          aria-busy={!localeError}
          onKeyDown={(event) => event.stopPropagation()}
        >
          <Logo />
          {localeError ? (
            <>
              <p role="alert">{localeError}</p>
              <button
                className="btn btn-primary"
                onClick={() => setLocaleAttempt((value) => value + 1)}
              >
                {t("重新加载", "再読み込み")}
              </button>
            </>
          ) : (
            <>
              <span className="spinner" />
              <p role="status">
                {t("正在加载词库…", "単語データを読み込み中…")}
              </p>
            </>
          )}
          <LanguagePicker />
        </div>
      )}
    </AtlasContext.Provider>
  );
}

function Shell({ privateAvailable }: { privateAvailable: boolean }) {
  const { t } = useI18n();
  const { route, word } = useLocation();
  const onboarded = useStore((s) => s.settings.onboarded);
  const theme = useStore((s) => s.settings.theme);
  const [palette, setPalette] = useState(false);
  const [splash, setSplash] = useState(shouldShowSplash);
  const focus = route.page === "learn";

  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      const typing = t.tagName === "INPUT" || t.tagName === "TEXTAREA";
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPalette((p) => !p);
      } else if (e.key === "/" && !typing && !focus) {
        e.preventDefault();
        setPalette(true);
      }
    };
    window.addEventListener("keydown", on);
    return () => window.removeEventListener("keydown", on);
  }, [focus]);

  useEffect(() => {
    if (!word) window.scrollTo({ top: 0 });
  }, [route.page]); // eslint-disable-line react-hooks/exhaustive-deps

  const dark =
    theme === "dark" ||
    (theme === "system" && matchMedia("(prefers-color-scheme: dark)").matches);

  const navLabel = (page: Route["page"], label: string) =>
    t(
      label,
      (
        {
          today: "今日",
          atlas: "図鑑",
          practice: "練習",
          me: "マイページ",
        } as Record<string, string>
      )[page] ?? label,
    );

  return (
    <div className={`app ${focus ? "is-focus" : ""}`}>
      {!focus && (
        <header className="topbar">
          <a
            className="topbar-logo"
            href="#/"
            aria-label={t("词光 Word Atlas 首页", "詞光 Word Atlas ホーム")}
          >
            <Logo />
          </a>
          <nav
            className="topnav"
            aria-label={t("主导航", "メインナビゲーション")}
          >
            {NAV.map(({ page, label }) => (
              <a
                key={page}
                href={page === "today" ? "#/" : `#/${page}`}
                className={route.page === page ? "is-on" : ""}
                aria-current={route.page === page ? "page" : undefined}
              >
                {navLabel(page, label)}
              </a>
            ))}
          </nav>
          <div className="topbar-tools">
            <button
              className="search-pill"
              onClick={() => setPalette(true)}
              aria-label={t("搜索单词", "単語を検索")}
            >
              <Search size={17} />
              <span>{t("搜索单词", "単語を検索")}</span>
              <kbd>⌘K</kbd>
            </button>
            <AmbiencePicker />
            <LanguagePicker />
            <button
              className="icon-btn"
              onClick={() => store.settings({ theme: dark ? "light" : "dark" })}
              aria-label={
                dark
                  ? t("切换到浅色", "ライトモードに切り替え")
                  : t("切换到深色", "ダークモードに切り替え")
              }
            >
              {dark ? <Sun size={19} /> : <Moon size={19} />}
            </button>
            <a
              className="icon-btn hide-sm"
              href="#/about"
              aria-label={t("关于与开源", "このアプリ・ソースコード")}
              title={t("关于与开源", "このアプリ・ソースコード")}
            >
              <Github size={19} />
            </a>
          </div>
        </header>
      )}

      <main className="main" id="main">
        {route.page === "today" && <Today />}
        {route.page === "atlas" && <AtlasPage route={route} />}
        {route.page === "learn" && <Learn />}
        {route.page === "practice" && <Practice />}
        {route.page === "me" && <Me privateAvailable={privateAvailable} />}
        {route.page === "about" && <About />}
      </main>

      {!focus && (
        <footer className="footer">
          <Logo compact />
          <p>
            {t(
              "一词一画，点亮雅思 · 免费开源 ·",
              "一語に一枚の絵、IELTSを照らす · 無料・オープンソース ·",
            )}{" "}
            <a href={REPO_URL} target="_blank" rel="noreferrer">
              GitHub
            </a>{" "}
            · <a href="#/about">{t("关于", "このアプリについて")}</a>
          </p>
        </footer>
      )}

      {!focus && (
        <nav
          className="tabbar"
          aria-label={t("主导航", "メインナビゲーション")}
        >
          {NAV.map(({ page, label, icon: Icon }) => (
            <a
              key={page}
              href={page === "today" ? "#/" : `#/${page}`}
              className={route.page === page ? "is-on" : ""}
              aria-current={route.page === page ? "page" : undefined}
            >
              <Icon size={22} strokeWidth={route.page === page ? 2.1 : 1.7} />
              <span>{navLabel(page, label)}</span>
            </a>
          ))}
        </nav>
      )}

      <WordSheet id={word} />
      <Palette open={palette} onClose={() => setPalette(false)} />
      {!onboarded && route.page !== "about" && !splash && <Onboarding />}
      {splash && <Splash onDone={() => setSplash(false)} />}
      <Toasts />
      <AmbienceController />
    </div>
  );
}

function WordSheet({ id }: { id: string | null }) {
  const { t } = useI18n();
  const atlas = useAtlas();
  const opened = id !== null;
  useEffect(() => {
    if (opened && store.get().settings.sfx) void cue("page");
  }, [opened]);
  const { entry, error } = useEntry(id);
  const ref = id ? atlas.byId.get(id) : undefined;
  const neighbor = useCallback(
    (d: number) => {
      if (!ref) return;
      const n = atlas.words[ref.order + d];
      if (n) go(currentLocation().route, n.id, true);
    },
    [atlas, ref],
  );
  useEffect(() => {
    if (!id) return;
    const on = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "INPUT") return;
      if (e.key === "ArrowLeft") neighbor(-1);
      if (e.key === "ArrowRight") neighbor(1);
    };
    window.addEventListener("keydown", on);
    return () => window.removeEventListener("keydown", on);
  }, [id, neighbor]);
  return (
    <Sheet
      open={!!id}
      onClose={closeWord}
      label={
        ref
          ? t(`${ref.word} 词条`, `${ref.word} の詳細`)
          : t("词条", "単語の詳細")
      }
      wide
    >
      {entry ? (
        <EntryView key={entry.id} entry={entry} />
      ) : error ? (
        <p className="sheet-error">{error}</p>
      ) : (
        <span className="spinner" />
      )}
      {ref && (
        <nav className="sheet-nav" aria-label={t("切换词条", "単語を切り替え")}>
          <button
            className="icon-btn"
            onClick={() => neighbor(-1)}
            disabled={ref.order === 0}
            aria-label={t("上一个", "前の単語")}
          >
            <ChevronLeft size={20} />
          </button>
          <span>
            {(ref.order + 1).toLocaleString()} / {atlas.count.toLocaleString()}
          </span>
          <button
            className="icon-btn"
            onClick={() => neighbor(1)}
            disabled={ref.order >= atlas.count - 1}
            aria-label={t("下一个", "次の単語")}
          >
            <ChevronRight size={20} />
          </button>
        </nav>
      )}
    </Sheet>
  );
}

export { openWord };
