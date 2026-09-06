import { NextResponse } from "next/server";
import { parseKanjiVg } from "@/lib/kanjivg";

export const revalidate = 86400;

const CODE = /^[0-9a-f]{5}$/;
const UA = "Levla/1.0 (kanji stroke-order; https://github.com/KanjiVG/kanjivg)";

const SOURCES = (code: string) => [
  `https://cdn.jsdelivr.net/gh/KanjiVG/kanjivg@master/kanji/${code}.svg`,
  `https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/${code}.svg`,
];

type Ctx = { params: Promise<{ code: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { code } = await ctx.params;
  if (!CODE.test(code)) {
    return NextResponse.json({ error: "invalid code" }, { status: 400 });
  }

  let svg = "";
  let found = false;
  for (const url of SOURCES(code)) {
    try {
      const res = await fetch(url, {
        headers: { "User-Agent": UA, Accept: "image/svg+xml,text/plain,*/*" },
        next: { revalidate },
      });
      if (res.status === 404) continue;
      if (!res.ok) continue;
      svg = await res.text();
      found = true;
      break;
    } catch {
      continue;
    }
  }

  if (!found || !svg.includes("<svg")) {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }

  const diagram = parseKanjiVg(svg);
  if (!diagram) {
    return NextResponse.json({ error: "unreadable" }, { status: 502 });
  }

  return NextResponse.json(diagram, {
    headers: {
      "Cache-Control": "public, max-age=86400, stale-while-revalidate=604800",
    },
  });
}
