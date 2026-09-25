/** True when this build is the static catalog (no Python backend). Opt in with NEXT_PUBLIC_DEMO=1. */
export function isDemo(): boolean {
  return process.env.NEXT_PUBLIC_DEMO === "1";
}
