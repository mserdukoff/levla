import type { NextConfig } from "next";

const backend = process.env.NLP_BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // The dev server blocks JS-chunk requests whose Origin doesn't match an
  // allowed host, as a DNS-rebinding guard — "localhost" is allowed by
  // default but the numeric loopback address is not. Visiting the app at
  // http://127.0.0.1:3000 then silently loses all client-side JS (fetches,
  // clicks, state) while the initial HTML still looks fine, which reads
  // exactly like "I saved something and it didn't show up."
  allowedDevOrigins: ["localhost", "127.0.0.1"],
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
