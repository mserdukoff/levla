import type { CefrLevel } from "@/lib/types";

export const BANDS: CefrLevel[] = ["A1", "A2", "B1", "B2"];

/**
 * The CEFR scale drawn as a small joined strip. The current band is inked;
 * the rest stay as hairline cells. This is how a level is shown everywhere
 * a level *matters* (placement, reader header). Where it is only metadata
 * (a shelf row) the band is plain serif text instead.
 */
export function BandStrip({
  level,
  inverted = false,
  className = "",
}: {
  level: CefrLevel | string;
  inverted?: boolean;
  className?: string;
}) {
  return (
    <span
      role="img"
      aria-label={`${level} on a scale of A1 to B2`}
      className={`inline-grid shrink-0 grid-cols-4 overflow-hidden rounded-[4px] border font-display text-[11px] leading-none tracking-[0.1em] ${
        inverted ? "divide-paper/25 border-paper/35" : "divide-ink/20 border-ink/30"
      } divide-x ${className}`}
    >
      {BANDS.map((band) => {
        const on = band === level;
        return (
          <span
            key={band}
            className={`px-[7px] py-[5px] text-center transition-colors ${
              on
                ? inverted
                  ? "bg-paper text-ink"
                  : "bg-ink text-paper"
                : inverted
                  ? "text-paper/55"
                  : "text-ink/45"
            }`}
          >
            {band}
          </span>
        );
      })}
    </span>
  );
}

/** A single hairline-boxed band label, used inside the gloss card. */
export function BandChip({ level }: { level: string }) {
  return (
    <span className="inline-flex h-[18px] items-center rounded-[3px] border border-ink/25 px-1.5 font-display text-[11px] leading-none tracking-[0.12em] text-ink/70">
      {level}
    </span>
  );
}
