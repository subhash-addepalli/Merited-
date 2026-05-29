"use client";
import { useState, useCallback } from "react";
import { InputForm } from "@/components/InputForm";
import { ProfileCard } from "@/components/ProfileCard";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { fetchProfile, refreshProfile } from "@/lib/api";
import { AppState } from "@/types";

export default function HomePage() {
  const [state, setState] = useState<AppState>({ status: "idle" });

  const handleSubmit = useCallback(async (username: string) => {
    setState({ status: "loading" });
    try {
      const data = await fetchProfile(username);
      setState({ status: "success", data });
      window.history.pushState({}, "", `/p/${username}`);
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Something went wrong",
      });
    }
  }, []);

  /**
   * Force a live re-fetch from GitHub, bypassing the cache.
   * Throws on failure so ProfileCard can show inline error.
   * On success, updates state in-place — no full reload.
   */
  const handleRefresh = useCallback(async () => {
    if (state.status !== "success") return;
    const username = state.data.username;
    const fresh = await refreshProfile(username); // throws on error — caught by ProfileCard
    setState({ status: "success", data: fresh });
  }, [state]);

  const handleReset = useCallback(() => {
    setState({ status: "idle" });
    window.history.pushState({}, "", "/");
  }, []);

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-white/5 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center">
              <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-base font-semibold tracking-tight">Merited</span>
          </div>
          <span className="text-xs text-white/25 font-mono hidden sm:block">
            GitHub → Hiring Decision
          </span>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        {state.status === "idle" && (
          <div className="w-full flex flex-col items-center gap-10 animate-fade-in">
            <div className="text-center space-y-3 max-w-xl">
              <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
                Turn GitHub into a{" "}
                <span className="text-emerald-400">hiring decision</span>
              </h1>
              <p className="text-white/40 text-base leading-relaxed">
                Enter a GitHub username. Get a recruiter-ready developer evaluation in seconds.
                No resumes. No guessing.
              </p>
            </div>
            <InputForm onSubmit={handleSubmit} loading={false} />
            <div className="flex items-center gap-6 text-xs text-white/20 flex-wrap justify-center">
              <span>✦ Real commit analysis</span>
              <span>✦ No account required</span>
              <span>✦ Shareable link</span>
            </div>
          </div>
        )}

        {state.status === "loading" && (
          <div className="w-full flex flex-col items-center gap-8">
            <InputForm onSubmit={handleSubmit} loading={true} />
            <LoadingSkeleton />
          </div>
        )}

        {state.status === "error" && (
          <div className="w-full flex flex-col items-center gap-8 animate-fade-in">
            <InputForm onSubmit={handleSubmit} loading={false} />
            <div className="w-full max-w-2xl mx-auto card p-6 border-red-500/20 bg-red-500/[0.03] text-center space-y-3">
              <div className="text-3xl">⚠️</div>
              <p className="text-white/70 font-medium">{state.message}</p>
              <button
                onClick={handleReset}
                className="text-sm text-white/40 hover:text-white transition-colors"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {state.status === "success" && (
          <div className="w-full flex flex-col items-center gap-6">
            <ProfileCard
              data={state.data}
              onReset={handleReset}
              onRefresh={handleRefresh}
            />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="flex-shrink-0 border-t border-white/5 py-4 px-6">
        <div className="max-w-2xl mx-auto flex items-center justify-between text-xs text-white/20">
          <span>Merited — Developer Evaluation Engine</span>
          <span className="font-mono">v1.0.0</span>
        </div>
      </footer>
    </main>
  );
}

