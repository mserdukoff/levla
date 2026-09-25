import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Landing, type LandingVariant } from "@/components/landing/landing";

const VARIANTS: LandingVariant[] = ["classic", "motion", "prompt", "story", "shader"];

export const metadata: Metadata = { robots: { index: false, follow: false } };

export function generateStaticParams() {
  return VARIANTS.map((variant) => ({ variant }));
}

export default async function VariantPage({ params }: { params: Promise<{ variant: string }> }) {
  const { variant } = await params;
  if (!VARIANTS.includes(variant as LandingVariant)) notFound();
  return <Landing variant={variant as LandingVariant} />;
}
