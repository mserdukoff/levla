"use client";

/**
 * A joined segmented control: one hairline box divided into cells.
 * The active cell inverts to ink. Used for language and CEFR level pickers.
 */
export function Segmented<T extends string>({
  options,
  value,
  onChange,
  columns,
  size = "md",
  ariaLabel,
}: {
  options: { id: T; label: string; hint?: string }[];
  value: T;
  onChange: (id: T) => void;
  columns?: number;
  size?: "sm" | "md";
  ariaLabel: string;
}) {
  const cols = columns ?? options.length;
  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className="grid overflow-hidden rounded-card border border-rule bg-paper-raised divide-x divide-rule"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {options.map((item) => {
        const active = item.id === value;
        return (
          <button
            key={item.id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(item.id)}
            className={`flex flex-col items-start text-left transition-colors ${
              size === "sm" ? "px-3 py-1.5" : "px-3.5 py-2.5"
            } ${active ? "bg-ink text-paper" : "text-ink hover:bg-paper-deep"}`}
          >
            <span
              className={
                size === "sm"
                  ? "text-[13px] font-medium leading-tight"
                  : "font-display text-[1.125rem] leading-none"
              }
            >
              {item.label}
            </span>
            {item.hint ? (
              <span
                className={`mt-1 text-[11px] leading-tight ${
                  active ? "text-paper/65" : "text-ink/45"
                }`}
              >
                {item.hint}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
