"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import { isSupabaseAuth } from "@/lib/supabase/env";
import type { MeResponse } from "@/lib/types";

export async function signOutAccount() {
  if (isSupabaseAuth()) {
    await createClient().auth.signOut();
  }
  await logout();
}

function authError(err: unknown): string {
  const raw = err instanceof Error ? err.message : "Something went wrong.";
  const text = raw.toLowerCase();
  if (text.includes("invalid login")) return "Email or password is wrong.";
  if (text.includes("already registered") || text.includes("already been registered")) {
    return "That email already has an account. Sign in instead.";
  }
  if (text.includes("password")) return raw;
  return raw;
}

export function AuthPanel({
  me,
  onRefresh,
  nextPath = "/library",
  layout = "shelf",
  redirectOnSuccess = false,
}: {
  me: MeResponse | null;
  onRefresh: () => void;
  nextPath?: string;
  layout?: "shelf" | "hero";
  redirectOnSuccess?: boolean;
}) {
  const router = useRouter();
  const [mode, setMode] = useState<"signup" | "signin">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function signOut() {
    await signOutAccount();
    onRefresh();
  }

  if (me?.authenticated) {
    if (layout === "hero") {
      return (
        <div id="account" className="mt-10 max-w-[22rem]">
          <p className="text-sm text-ink/55">
            Signed in as {me.display_name || me.email}
          </p>
          <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-3">
            <Link href={nextPath} className="btn-primary">
              Start reading
            </Link>
            {me.admin ? (
              <Link href="/admin" className="t-quiet">
                Admin
              </Link>
            ) : null}
            <button type="button" onClick={() => void signOut()} className="t-quiet">
              Sign out
            </button>
          </div>
        </div>
      );
    }
    return (
      <div className="flex items-baseline justify-between gap-3 border-y border-rule py-3 text-sm text-ink/60">
        <p className="min-w-0 truncate">{me.display_name || me.email}</p>
        <div className="flex shrink-0 items-baseline gap-4">
          {me.admin ? (
            <Link href="/admin" className="t-quiet underline decoration-ink/20 underline-offset-4">
              Admin
            </Link>
          ) : null}
          <button
            type="button"
            onClick={() => void signOut()}
            className="t-quiet underline decoration-ink/20 underline-offset-4"
          >
            Sign out
          </button>
        </div>
      </div>
    );
  }

  async function submit() {
    setBusy(true);
    setMessage(null);
    try {
      if (!isSupabaseAuth()) {
        throw new Error("Accounts are not configured in this environment.");
      }
      if (mode === "signup" && password !== confirm) {
        throw new Error("Passwords do not match.");
      }
      if (password.length < 8) {
        throw new Error("Use at least 8 characters.");
      }
      const supabase = createClient();
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        if (!data.session) {
          throw new Error(
            "The account was created, but email confirmation is still on. Turn Confirm email off in Supabase Auth, then sign in.",
          );
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
      onRefresh();
      if (redirectOnSuccess) router.push(nextPath);
    } catch (err) {
      setMessage(authError(err));
    } finally {
      setBusy(false);
    }
  }

  const heading = mode === "signup" ? "Create an account" : "Sign in";
  const action = mode === "signup" ? "Create account" : "Sign in";
  const wrap =
    layout === "hero"
      ? "mt-10 max-w-[22rem] scroll-mt-10"
      : "flex flex-col gap-3 border-y border-rule py-5";

  return (
    <form
      id="account"
      className={wrap}
      onSubmit={async (e) => {
        e.preventDefault();
        await submit();
      }}
    >
      {layout === "hero" ? (
        <h2 className="font-display text-[1.35rem] text-ink">{heading}</h2>
      ) : (
        <p className="text-sm text-ink/55">
          {mode === "signup"
            ? "Create an account to keep progress across devices"
            : "Sign in to keep progress across devices"}
          {me?.require_auth ? " and to restock custom texts." : "."}
        </p>
      )}
      {layout === "hero" ? (
        <p className="mt-2 text-sm leading-relaxed text-ink/55">
          An email and a password. Progress stays with the account.
        </p>
      ) : null}
      <div className={layout === "hero" ? "mt-5 flex flex-col gap-3" : "flex flex-col gap-3"}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          autoComplete="email"
          required
          className="field-line text-sm!"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          autoComplete={mode === "signup" ? "new-password" : "current-password"}
          minLength={8}
          required
          className="field-line text-sm!"
        />
        {mode === "signup" ? (
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="Confirm password"
            autoComplete="new-password"
            minLength={8}
            required
            className="field-line text-sm!"
          />
        ) : null}
        <button type="submit" disabled={busy} className="btn-primary mt-1 h-11 w-full text-[15px]">
          {busy ? "One moment…" : action}
        </button>
      </div>
      <button
        type="button"
        disabled={busy}
        onClick={() => {
          setMode(mode === "signup" ? "signin" : "signup");
          setMessage(null);
        }}
        className="t-quiet mt-4 self-start text-sm"
      >
        {mode === "signup" ? "Already have an account? Sign in" : "New here? Create an account"}
      </button>
      {message ? <p className="mt-3 text-[13px] leading-relaxed text-terracotta">{message}</p> : null}
    </form>
  );
}
