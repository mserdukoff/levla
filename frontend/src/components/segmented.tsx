"use client";

import { motion } from "motion/react";
import { useId } from "react";

/**
 * A joined segmented control: one hairline box divided into cells.
 * The active cell inverts to ink. Used for language and CEFR level pickers.
 * `animated` slides the ink fill between cells instead of swapping it.
 */
export function Segmented<T extends string>({
  options,
  value,
  onChange,
  columns,
  size = "md",
  ariaLabel,
  animated = false,
}: {
  options: { id: T; label: string; hint?: string }[];
  value: T;
  onChange: (id: T) => void;
  columns?: number;
  size?: "sm" | "md";
  ariaLabel: string;
  animated?: boolean;
}) {
  const cols = columns ?? options.length;
  const pill = useId();
  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className="grid overflow-hidden rounded-card border border-rule bg-paper-raised divide-x divide-rule"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {options.map((item) => {
        const active = item.id === value;
        const fill = active && !animated ? "bg-ink" : "";
        const hover = active ? "" : "hover:bg-paper-deep";
        return (
          <button
            key={item.id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(item.id)}
            className={`relative flex flex-col items-start text-left transition-colors duration-300 ${
              size === "sm" ? "px-3 py-1.5" : "px-3.5 py-2.5"
            } ${active ? "text-paper" : "text-ink"} ${fill} ${hover}`}
          >
            {animated && active ? (
              <motion.span
                layoutId={pill}
                aria-hidden="true"
                className="absolute inset-0 bg-ink"
                transition={{ type: "spring", stiffness: 420, damping: 36 }}
              />
            ) : null}
            <span
              className={`relative ${
                size === "sm"
                  ? "text-[13px] font-medium leading-tight"
                  : "font-display text-[1.125rem] leading-none"
              }`}
            >
              {item.label}
            </span>
            {item.hint ? (
              <span
                className={`relative mt-1 text-[11px] leading-tight ${
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
