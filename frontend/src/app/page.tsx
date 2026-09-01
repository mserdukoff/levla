import { Shelf } from "@/components/shelf";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-full w-full max-w-[34rem] flex-col px-5 py-16 sm:px-8">
      <p className="font-display text-[13px] uppercase tracking-[0.28em] text-terracotta">
        Russian · Japanese · A1–B2
      </p>
      <h1 className="mt-3 font-display text-6xl font-medium tracking-tight text-ink">
        Levla
      </h1>
      <p className="mt-4 max-w-md text-lg leading-relaxed text-ink/70">
        Graded readers at a real CEFR level. Pick a text. Too easy, just right,
        or too hard decides the next one.
      </p>
      <div className="mt-12">
        <Shelf />
      </div>
    </main>
  );
}
