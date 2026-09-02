import type { Metadata } from "next";
import { Shelf } from "@/components/shelf";

export const metadata: Metadata = {
  title: "Library",
};

export default function LibraryPage() {
  return (
    <main className="mx-auto flex min-h-full w-full max-w-[36rem] flex-col px-5 pb-24 pt-8 sm:px-8 sm:pt-10">
      <Shelf />
    </main>
  );
}
