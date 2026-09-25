"use client";

import { useEffect } from "react";
import { isDemo } from "@/lib/demo";
import { deviceHeaders } from "@/lib/device";
import { isSupabaseAuth } from "@/lib/supabase/env";
import { createClient } from "@/lib/supabase/client";

/** After Supabase sign-in, attach this browser's guest progress to the account. */
export function AuthBridge() {
  useEffect(() => {
    if (isDemo() || !isSupabaseAuth()) return;
    const supabase = createClient();

    async function attach() {
      await fetch("/api/auth/session", {
        method: "POST",
        credentials: "include",
        headers: deviceHeaders(true),
        body: "{}",
      }).catch(() => undefined);
    }

    void supabase.auth.getClaims().then(({ data }) => {
      if (data?.claims) void attach();
    });

    const { data } = supabase.auth.onAuthStateChange((event) => {
      if (event === "SIGNED_IN") void attach();
    });
    return () => data.subscription.unsubscribe();
  }, []);
  return null;
}
