/** True when this build is the static Vercel demo (no Python backend). */
export function isDemo(): boolean {
  return process.env.NEXT_PUBLIC_DEMO === "1";
}
