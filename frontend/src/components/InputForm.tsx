"use client";
import { useState, FormEvent } from "react";

interface InputFormProps {
  onSubmit: (username: string) => void;
  loading: boolean;
}

const SAMPLE_USERS = ["torvalds", "gaearon", "yyx990803", "antirez", "sindresorhus"];

export function InputForm({ onSubmit, loading }: InputFormProps) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim().replace(/^@/, "");
    if (trimmed) onSubmit(trimmed);
  }

  return (
    <div className="w-full max-w-xl mx-auto space-y-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-white/[0.06] border border-white/10 focus-within:border-emerald-500/50 transition-colors">
          {/* GitHub icon */}
          <div className="flex-shrink-0 pl-3">
            <svg className="w-5 h-5 text-white/40" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
            </svg>
          </div>

          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Enter GitHub username..."
            className="flex-1 bg-transparent text-white placeholder-white/30 text-sm font-mono outline-none py-2.5 px-1"
            disabled={loading}
            autoComplete="off"
            spellCheck={false}
          />

          <button
            type="submit"
            disabled={loading || !value.trim()}
            className="flex-shrink-0 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:bg-white/10 disabled:text-white/30 text-sm font-semibold text-black transition-all duration-150 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing
              </span>
            ) : (
              "Analyze →"
            )}
          </button>
        </div>
      </form>

      {/* Sample users */}
      <div className="flex items-center gap-2 flex-wrap justify-center">
        <span className="text-xs text-white/25">Try:</span>
        {SAMPLE_USERS.map((u) => (
          <button
            key={u}
            onClick={() => {
              setValue(u);
              onSubmit(u);
            }}
            disabled={loading}
            className="text-xs text-white/40 hover:text-emerald-400 font-mono transition-colors disabled:pointer-events-none"
          >
            @{u}
          </button>
        ))}
      </div>
    </div>
  );
}
