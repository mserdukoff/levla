import type { Metadata } from "next";
import Link from "next/link";
import { Art } from "@/components/landing/art";

export const metadata: Metadata = {
  title: "Privacy",
};

export default function PrivacyPage() {
  return (
    <main className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pb-24 pt-8 sm:px-8 sm:pt-10">
      <Link href="/" className="t-quiet">
        ← Lociros
      </Link>
      <Art src="hills-strip" className="-mb-4 ml-auto mt-2 w-[18rem] opacity-80" />
      <h1 className="t-heading mt-10 text-[2rem] text-ink">Privacy</h1>
      <div className="mt-8 flex max-w-[34rem] flex-col gap-5 text-[1.0625rem] leading-[1.65] text-ink/80">
        <p>
          This browser keeps a device id, the language you last chose, and whether grammar color,
          furigana, and fading known words are on.
        </p>
        <p>
          In the demo, your level, the passages you have rated, and the words you save stay in this
          browser. The demo has no account to send them to.
        </p>
        <p>If you create an account, your email is stored with the library for that account.</p>
      </div>
    </main>
  );
}
