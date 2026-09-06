"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { fetchStrokeDiagram, peekStrokeDiagram, type StrokeDiagram } from "@/lib/kanjivg";

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Slow enough to follow with a finger; short ticks stay readable, long ones don't drag. */
function durationFor(length: number): number {
  return Math.min(1100, Math.max(520, length * 10));
}

const START_MS = 200;
const GAP_MS = 220;
const END_MS = 80;

/**
 * KanjiVG stroke diagram. Faint traces of the whole character sit underneath;
 * ink strokes draw in order, with numbers appearing as each stroke starts.
 * `replay` changing starts the animation over.
 */
export function StrokeOrder({
  char,
  replay = 0,
  fallback,
}: {
  char: string;
  replay?: number;
  fallback: string;
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [diagram, setDiagram] = useState<StrokeDiagram | null>(
    () => peekStrokeDiagram(char) ?? null,
  );
  const [missing, setMissing] = useState(() => peekStrokeDiagram(char) === null);

  useEffect(() => {
    let cancelled = false;
    setMissing(false);
    fetchStrokeDiagram(char).then((next) => {
      if (cancelled) return;
      if (next) setDiagram(next);
      else setMissing(true);
    });
    return () => {
      cancelled = true;
    };
  }, [char]);

  useLayoutEffect(() => {
    const svg = svgRef.current;
    if (!svg || !diagram) return;

    const strokes = [
      ...svg.querySelectorAll<SVGPathElement>("[data-stroke]"),
    ];
    const labels = [...svg.querySelectorAll<SVGTextElement>("[data-n]")];
    if (strokes.length === 0) return;

    const lengths = strokes.map((path) => path.getTotalLength());
    const setOffset = (i: number, offset: number) => {
      const path = strokes[i];
      path.style.strokeDasharray = `${lengths[i]}`;
      path.style.strokeDashoffset = `${offset}`;
    };
    const setLabel = (i: number, on: boolean) => {
      const label = labels[i];
      if (label) label.style.opacity = on ? "1" : "0";
    };

    if (prefersReducedMotion()) {
      strokes.forEach((_, i) => {
        setOffset(i, 0);
        setLabel(i, true);
      });
      return;
    }

    strokes.forEach((_, i) => {
      setOffset(i, lengths[i]);
      setLabel(i, false);
    });

    const spans = strokes.map((_, i) => ({
      i,
      start: 0,
      dur: durationFor(lengths[i]),
    }));
    let cursor = START_MS;
    for (const span of spans) {
      span.start = cursor;
      cursor += span.dur + GAP_MS;
    }
    const total = cursor + END_MS;

    let frame = 0;
    let cancelled = false;
    let started = false;
    let origin = 0;

    const tick = (now: number) => {
      if (cancelled) return;
      const elapsed = now - origin;
      for (const span of spans) {
        if (elapsed < span.start) continue;
        setLabel(span.i, true);
        const p = Math.min(1, (elapsed - span.start) / span.dur);
        const eased = 1 - (1 - p) ** 3;
        setOffset(span.i, lengths[span.i] * (1 - eased));
      }
      if (elapsed < total) frame = requestAnimationFrame(tick);
    };

    const play = () => {
      if (cancelled || started) return;
      started = true;
      origin = performance.now();
      frame = requestAnimationFrame(tick);
    };

    const visible = () => {
      const box = svg.getBoundingClientRect();
      return box.bottom > 0 && box.top < window.innerHeight;
    };

    if (visible()) play();
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) play();
      },
      { threshold: 0.35 },
    );
    io.observe(svg);

    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      io.disconnect();
    };
  }, [diagram, replay]);

  if (missing) {
    return (
      <span className="font-ja text-[1.75rem] leading-none text-ink">
        {fallback}
      </span>
    );
  }
  if (!diagram) {
    return <span className="block h-[6.75rem] w-[6.75rem] border border-rule" aria-hidden="true" />;
  }

  return (
    <svg
      ref={svgRef}
      viewBox={diagram.viewBox}
      className="block h-[6.75rem] w-[6.75rem] border border-rule text-ink"
      aria-hidden="true"
    >
      <g
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-ink/15"
      >
        {diagram.paths.map((d, i) => (
          <path key={`trace-${i}`} d={d} />
        ))}
      </g>
      <g
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {diagram.paths.map((d, i) => (
          <path key={`stroke-${i}`} d={d} data-stroke={i} />
        ))}
      </g>
      <g
        className="fill-ink/50"
        fontSize="11"
        fontFamily="var(--sans)"
        style={{ fontVariantNumeric: "tabular-nums" }}
      >
        {diagram.numbers.map((num, i) => (
          <text
            key={num.n}
            x={num.x}
            y={num.y}
            data-n={i}
            style={{ opacity: 0 }}
          >
            {num.n}
          </text>
        ))}
      </g>
    </svg>
  );
}

export function StrokeOrderButton({
  char,
  className = "",
}: {
  char: string;
  className?: string;
}) {
  const [replay, setReplay] = useState(0);
  return (
    <button
      type="button"
      aria-label={`Replay stroke order for ${char}`}
      onClick={() => setReplay((n) => n + 1)}
      className={`shrink-0 cursor-pointer select-none rounded-[3px] bg-transparent p-0 text-left transition-colors hover:bg-ink/[0.07] ${className}`}
    >
      <StrokeOrder char={char} replay={replay} fallback={char} />
    </button>
  );
}
