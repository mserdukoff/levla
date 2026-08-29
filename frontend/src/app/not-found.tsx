import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-full max-w-md flex-col justify-center px-5 py-24">
      <h1 className="font-display text-3xl text-ink">Passage gone</h1>
      <p className="mt-3 text-ink/60">
        That reader was not found. Generate a new one.
      </p>
      <Link
        href="/"
        className="mt-8 text-sm text-terracotta underline underline-offset-4"
      >
        Back to Levla
      </Link>
    </main>
  );
}
