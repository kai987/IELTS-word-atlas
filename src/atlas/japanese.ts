import type { Atlas, Entry } from "./types";

export interface JapaneseEntry {
  id: string;
  senses: string[];
  ex: string[];
  col: string[];
  tip: string;
  note: string;
  fam?: string[];
  syn?: string[];
  ant?: string[];
}

const TOPICS: Record<string, string> = {
  education: "教育",
  work: "仕事",
  technology: "テクノロジー",
  science: "科学",
  environment: "環境",
  health: "健康",
  society: "社会",
  government: "政治・法律",
  economy: "経済",
  media: "メディア",
  arts: "芸術",
  travel: "旅行",
  city: "都市",
  nature: "自然",
  daily: "暮らし",
  emotion: "感情",
  thinking: "思考",
  sport: "スポーツ",
  history: "歴史",
};
const BASE = (import.meta.env?.BASE_URL ?? "/").replace(/\/$/, "");
const cached = new WeakMap<Atlas, Promise<Atlas>>();

/** Keep stable IDs/media and the Chinese source intact; localize display fields only. */
export function applyJapaneseEntry(source: Entry, ja: JapaneseEntry): Entry {
  if (
    source.id !== ja.id ||
    source.senses.length !== ja.senses.length ||
    source.ex.length !== ja.ex.length ||
    source.col.length !== ja.col.length ||
    (["fam", "syn", "ant"] as const).some(
      (key) => ja[key] !== undefined && ja[key]!.length !== source[key].length,
    )
  )
    throw new Error(`日本語データの形式が一致しません：${source.id}`);
  return {
    ...source,
    senses: source.senses.map((sense, index) => ({
      ...sense,
      zh: ja.senses[index],
    })),
    ex: source.ex.map((example, index) => ({ ...example, zh: ja.ex[index] })),
    col: ja.col,
    tip: ja.tip,
    note: ja.note,
    fam: ja.fam ?? source.fam,
    syn: ja.syn ?? source.syn,
    ant: ja.ant ?? source.ant,
  };
}

export function loadJapaneseAtlas(source: Atlas): Promise<Atlas> {
  const hit = cached.get(source);
  if (hit) return hit;
  const pending = createJapaneseAtlas(source).catch((error) => {
    cached.delete(source);
    throw error;
  });
  cached.set(source, pending);
  return pending;
}

async function createJapaneseAtlas(source: Atlas): Promise<Atlas> {
  if (source.kind !== "open")
    throw new Error(
      "このローカル単語帳には日本語データがありません。中国語に切り替えてください。",
    );
  const response = await fetch(`${BASE}/atlas/ja/index.json`);
  if (!response.ok)
    throw new Error(
      `日本語の単語データを読み込めませんでした（${response.status}）`,
    );
  const index = (await response.json()) as {
    chunk: number;
    words: Record<string, string>;
  };
  if (!Number.isInteger(index.chunk) || index.chunk < 1)
    throw new Error("日本語データの分割サイズが無効です。");
  const words = source.words.map((word) => {
    const meaning = index.words[word.id];
    if (!meaning) throw new Error(`日本語の意味が見つかりません：${word.word}`);
    return { ...word, zh: meaning };
  });
  const byId = new Map(words.map((word) => [word.id, word]));
  const entries = new Map<string, Entry>();
  const chunks = new Map<number, Promise<Map<string, JapaneseEntry>>>();
  const loadChunk = (number: number) => {
    let pending = chunks.get(number);
    if (!pending) {
      pending = fetch(`${BASE}/atlas/ja/entries/${number}.json`)
        .then(async (response) => {
          if (!response.ok)
            throw new Error(
              `日本語の単語詳細を読み込めませんでした（${response.status}）`,
            );
          const rows = (await response.json()) as JapaneseEntry[];
          return new Map(rows.map((row) => [row.id, row]));
        })
        .catch((error) => {
          chunks.delete(number);
          throw error;
        });
      chunks.set(number, pending);
    }
    return pending;
  };
  return {
    ...source,
    words,
    byId,
    topics: source.topics.map(([key]) => [key, TOPICS[key] ?? key]),
    peek: (id) => entries.get(id),
    async entry(id) {
      const hit = entries.get(id);
      if (hit) return hit;
      const ref = byId.get(id);
      if (!ref) throw new Error(`単語が見つかりません：${id}`);
      const [original, chunk] = await Promise.all([
        source.entry(id),
        loadChunk(Math.floor(ref.order / index.chunk)),
      ]);
      const translation = chunk.get(id);
      if (!translation)
        throw new Error(`日本語の単語詳細が見つかりません：${id}`);
      const entry = applyJapaneseEntry(original, translation);
      entries.set(id, entry);
      return entry;
    },
  };
}
