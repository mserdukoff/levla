export type StrokeNumber = { x: number; y: number; n: string };

export type StrokeDiagram = {
  viewBox: string;
  paths: string[];
  numbers: StrokeNumber[];
};

const inflight = new Map<string, Promise<StrokeDiagram | null>>();
const resolved = new Map<string, StrokeDiagram | null>();

/** KanjiVG files are named with a 5-digit lowercase hex codepoint. */
export function kanjiHex(char: string): string | null {
  const cp = char.codePointAt(0);
  if (cp == null) return null;
  return cp.toString(16).padStart(5, "0");
}

export function parseKanjiVg(svg: string): StrokeDiagram | null {
  const viewBox = svg.match(/\bviewBox="([^"]+)"/)?.[1] ?? "0 0 109 109";
  const afterPaths = svg.split(/id="kvg:StrokePaths_[^"]*"/)[1];
  if (!afterPaths) return null;
  const pathSection = afterPaths.split(/id="kvg:StrokeNumbers/)[0];
  const paths = [...pathSection.matchAll(/\bd="([^"]+)"/g)].map((m) => m[1]);
  if (paths.length === 0) return null;

  const afterNumbers = svg.split(/id="kvg:StrokeNumbers_[^"]*"/)[1] ?? "";
  const numbers = [
    ...afterNumbers.matchAll(
      /<text\b[^>]*transform="matrix\(1 0 0 1 ([0-9.]+) ([0-9.]+)\)"[^>]*>\s*(\d+)\s*<\/text>/g,
    ),
  ].map((m) => ({ x: Number(m[1]), y: Number(m[2]), n: m[3] }));

  return { viewBox, paths, numbers };
}

async function loadDiagram(code: string): Promise<StrokeDiagram | null> {
  try {
    const res = await fetch(`/kanji-strokes/${code}`);
    if (!res.ok) {
      resolved.set(code, null);
      return null;
    }
    const data = (await res.json()) as StrokeDiagram;
    if (!data?.paths?.length) {
      resolved.set(code, null);
      return null;
    }
    resolved.set(code, data);
    return data;
  } catch {
    resolved.set(code, null);
    return null;
  }
}

export function peekStrokeDiagram(char: string): StrokeDiagram | null | undefined {
  const code = kanjiHex(char);
  if (!code) return null;
  if (!resolved.has(code)) return undefined;
  return resolved.get(code);
}

export function fetchStrokeDiagram(char: string): Promise<StrokeDiagram | null> {
  const code = kanjiHex(char);
  if (!code) return Promise.resolve(null);
  if (resolved.has(code)) return Promise.resolve(resolved.get(code) ?? null);
  let hit = inflight.get(code);
  if (!hit) {
    hit = loadDiagram(code);
    inflight.set(code, hit);
  }
  return hit;
}
