import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { supabasePublishableKey, supabaseUrl } from "./env";

export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(supabaseUrl(), supabasePublishableKey(), {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet, _headers) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options),
          );
        } catch {
          // Called from a Server Component. The Proxy writes cookies.
        }
      },
    },
  });
}

export async function accessToken(): Promise<string | null> {
  if (!supabaseUrl() || !supabasePublishableKey()) return null;
  const supabase = await createClient();
  await supabase.auth.getClaims();
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}
