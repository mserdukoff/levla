import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-full max-w-md flex-col justify-center px-5 py-24">
      <p className="t-kicker">Levla</p>
      <h1 className="t-heading mt-4 text-[2rem] text-ink">Passage gone</h1>
      <p className="mt-3 text-ink/60">That reader was not found. Pick another from the shelf.</p>
      <Link
        href="/library"
        className="mt-8 self-start text-sm text-terracotta underline decoration-terracotta/40 underline-offset-4"
      >
        Back to the library
      </Link>
    </main>
  );
}
