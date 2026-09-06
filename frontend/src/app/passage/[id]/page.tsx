import { notFound } from "next/navigation";
import { Reader } from "@/components/reader";
import { backendUrl } from "@/lib/backend";
import type { Passage } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function PassagePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const res = await fetch(`${backendUrl()}/api/passages/${id}`, { cache: "no-store" });
  if (res.status === 404) notFound();
  if (!res.ok) {
    throw new Error(`Could not load passage (${res.status})`);
  }
  const passage: Passage = await res.json();
  return <Reader passage={passage} />;
}
