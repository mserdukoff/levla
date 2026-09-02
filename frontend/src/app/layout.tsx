import type { Metadata } from "next";
import { Literata, Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
});

// Variable Literata with its optical-size axis, so the same face sets
// 11px labels and 64px display without looking like two fonts.
const literata = Literata({
  variable: "--font-literata",
  subsets: ["latin", "cyrillic"],
  axes: ["opsz"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Levla — graded readers",
    template: "%s · Levla",
  },
  description:
    "CEFR-calibrated Russian and Japanese passages. The level is checked by a morphological analyzer, not promised by a prompt. Tap any word for lemma, grammar, and a gloss.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "Levla",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${literata.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-paper text-ink">
        {children}
        <script
          // Only register the offline cache in production. In dev the app
          // changes under you constantly, and a service worker happily
          // keeps serving yesterday's JS and API responses over that —
          // "I did X and it doesn't show up" with no error anywhere. Any
          // worker left over from an earlier dev session gets torn down
          // here too, along with its caches, so a stale one can't linger.
          dangerouslySetInnerHTML={{
            __html: `if("serviceWorker"in navigator){if(${
              process.env.NODE_ENV === "production"
            }){window.addEventListener("load",()=>navigator.serviceWorker.register("/sw.js"))}else{navigator.serviceWorker.getRegistrations().then(rs=>rs.forEach(r=>r.unregister()));if(window.caches)caches.keys().then(ks=>ks.forEach(k=>caches.delete(k)))}}`,
          }}
        />
      </body>
    </html>
  );
}
