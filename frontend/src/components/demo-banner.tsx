import { isDemo } from "@/lib/demo";

export function DemoBanner() {
  if (!isDemo()) return null;
  return (
    <p className="py-1 text-[13px] leading-relaxed text-ink/55">
      Static demo — a fixed catalog, no accounts, no custom generation. Ratings and saved words
      stay in this browser.
    </p>
  );
}
