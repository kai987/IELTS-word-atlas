import { createContext, useContext, useEffect, useState } from "react";
import type { Atlas, Entry } from "./types";

export const AtlasContext = createContext<Atlas | null>(null);

export function useAtlas() {
  const a = useContext(AtlasContext);
  if (!a) throw new Error("Atlas not loaded");
  return a;
}

/** Full entry for an id; returns the cached copy synchronously when available. */
export function useEntry(id: string | null | undefined) {
  const atlas = useAtlas();
  const [result, setResult] = useState<{
    atlas: Atlas;
    id: typeof id;
    entry?: Entry;
    error: string | null;
  }>(() => ({
    atlas,
    id,
    entry: id ? atlas.peek(id) : undefined,
    error: null,
  }));
  useEffect(() => {
    if (!id) return;
    const hit = atlas.peek(id);
    setResult({ atlas, id, entry: hit, error: null });
    if (hit) return;
    let live = true;
    atlas.entry(id).then(
      (entry) => {
        if (live) setResult({ atlas, id, entry, error: null });
      },
      (error: Error) => {
        if (live) setResult({ atlas, id, error: error.message });
      },
    );
    return () => {
      live = false;
    };
  }, [atlas, id]);
  const current = result.atlas === atlas && result.id === id;
  return {
    entry:
      (id ? atlas.peek(id) : undefined) ?? (current ? result.entry : undefined),
    error: current ? result.error : null,
  };
}

/** Warm the chunks for a list of ids (e.g. a learning session). */
export function prefetch(atlas: Atlas, ids: string[]) {
  return Promise.all(ids.map((id) => atlas.entry(id).catch(() => null)));
}
