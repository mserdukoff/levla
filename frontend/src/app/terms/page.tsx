import type { Metadata } from "next";
import Link from "next/link";
import { Art } from "@/components/landing/art";

export const metadata: Metadata = {
  title: "Terms",
};

export default function TermsPage() {
  return (
    <main className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pb-24 pt-8 sm:px-8 sm:pt-10">
      <Link href="/" className="t-quiet">
        ← Lociros
      </Link>
      <Art src="hills-strip" className="-mb-4 ml-auto mt-2 w-[18rem] opacity-80" />
      <h1 className="t-heading mt-10 text-[2rem] text-ink">Terms</h1>
      <div className="mt-8 flex max-w-[34rem] flex-col gap-5 text-[1.0625rem] leading-[1.65] text-ink/80">
        <p>
          Lociros is a reading-practice demo. The passages are short graded texts for study. They
          are not a course, a certificate, or a substitute for a teacher.
        </p>
        <p>
          The demo has no accounts, no billing, and no sync between browsers. What you rate and
          save stays in the browser you used.
        </p>
        <p>
          A passage can still be wrong. The level check reads every word mechanically, and it can
          miss something or flag something it should not.
        </p>
      </div>
    </main>
  );
}
