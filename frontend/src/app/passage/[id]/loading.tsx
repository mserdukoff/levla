import Link from "next/link";

/** Static composition, no shimmer: a title rule and a few text lines. */
export default function PassageLoading() {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pt-7 sm:px-8 sm:pt-9">
      <header className="flex items-center justify-between gap-4">
        <Link href="/library" className="t-quiet">
          ← Library
        </Link>
        <div className="h-[22px] w-[104px] rounded-[4px] border border-rule" />
      </header>
      <div className="mt-12 sm:mt-14">
        <div className="h-2.5 w-24 rounded-[2px] bg-rule/70" />
        <div className="mt-5 h-8 w-3/4 rounded-[3px] bg-rule/80" />
      </div>
      <div className="mt-8 border-y border-rule py-3">
        <div className="flex gap-5">
          <div className="h-2.5 w-12 rounded-[2px] bg-rule/60" />
          <div className="h-2.5 w-14 rounded-[2px] bg-rule/60" />
          <div className="h-2.5 w-14 rounded-[2px] bg-rule/60" />
        </div>
      </div>
      <div className="mt-10 space-y-4">
        <div className="h-4 w-full rounded-[2px] bg-rule/55" />
        <div className="h-4 w-11/12 rounded-[2px] bg-rule/55" />
        <div className="h-4 w-full rounded-[2px] bg-rule/55" />
        <div className="h-4 w-4/5 rounded-[2px] bg-rule/55" />
        <div className="h-4 w-2/3 rounded-[2px] bg-rule/55" />
      </div>
    </div>
  );
}
