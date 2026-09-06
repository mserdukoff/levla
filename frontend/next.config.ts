import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const frontendDir = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: frontendDir,
  turbopack: { root: frontendDir },
  // The dev server blocks JS-chunk requests whose Origin doesn't match an
  // allowed host, as a DNS-rebinding guard — "localhost" is allowed by
  // default but the numeric loopback address is not. Visiting the app at
  // http://127.0.0.1:3000 then silently loses all client-side JS (fetches,
  // clicks, state) while the initial HTML still looks fine, which reads
  // exactly like "I saved something and it didn't show up."
  allowedDevOrigins: ["localhost", "127.0.0.1"],
};

export default nextConfig;
