"use client";
import { useState } from "react";
import Link from "next/link";
import { ProfileData } from "@/types";
import { ProfileCard } from "@/components/ProfileCard";
import { fetchProfile, refreshProfile } from "@/lib/api";

interface Props {
  profile: ProfileData | null;
  username: string;
}

export default function SharedProfileClient({ profile: initialProfile, username }: Props) {
  const [profile, setProfile] = useState(initialProfile);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState("");

  async function analyze() {
    setLoading(true);
    setError("");
    try {
      const data = await fetchProfile(username);
      setProfile(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    const fresh = await refreshProfile(username); // throws — caught by ProfileCard
    setProfile(fresh);
  }

  if (!profile && !loading) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-6 px-4">
        <div className="text-center space-y-3">
          <p className="text-5xl">🔍</p>
          <h1 className="text-xl font-semibold text-white">Profile not found</h1>
          <p className="text-white/40 text-sm">@{username} hasn&apos;t been analyzed yet.</p>
        </div>
        <button
          onClick={analyze}
          className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-black text-sm font-semibold rounded-xl transition-colors"
        >
          Analyze @{username}
        </button>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <Link href="/" className="text-sm text-white/30 hover:text-white transition-colors">
          ← Back to Merited
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col">
      <header className="flex-shrink-0 border-b border-white/5 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center">
              <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-base font-semibold tracking-tight">Merited</span>
          </Link>
          <Link href="/" className="text-xs text-white/30 hover:text-white transition-colors">
            Analyze another →
          </Link>
        </div>
      </header>

      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        {loading ? (
          <p className="text-white/40 text-sm animate-pulse">Analyzing @{username}…</p>
        ) : profile ? (
          <ProfileCard
            data={profile}
            onReset={() => (window.location.href = "/")}
            onRefresh={handleRefresh}
          />
        ) : null}
      </div>
    </main>
  );
}

