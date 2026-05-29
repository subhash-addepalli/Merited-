"use client";
import { useState } from "react";
import Image from "next/image";
import { ProfileData } from "@/types";
import { ScoreBar } from "./ScoreBar";
import { getShareUrl } from "@/lib/api";

interface ProfileCardProps {
  data: ProfileData;
  onReset: () => void;
  onRefresh: () => Promise<void>;
}

// ── Small primitives ──────────────────────────────────────────────────────────

const FEATURE_COLORS: Record<string, string> = {
  Authentication:         "bg-violet-500/15 text-violet-300 border-violet-500/20",
  "Database Integration": "bg-blue-500/15 text-blue-300 border-blue-500/20",
  "REST API":             "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
  Docker:                 "bg-cyan-500/15 text-cyan-300 border-cyan-500/20",
  "CI/CD":                "bg-orange-500/15 text-orange-300 border-orange-500/20",
  Tests:                  "bg-pink-500/15 text-pink-300 border-pink-500/20",
};

function TechBadge({ tech }: { tech: string }) {
  const colors = FEATURE_COLORS[tech] || "bg-white/5 text-white/60 border-white/10";
  return <span className={`badge border text-xs ${colors}`}>{tech}</span>;
}

function getRoleIcon(role: string): string {
  const r = role.toLowerCase();
  if (r.includes("backend"))  return "⚙️";
  if (r.includes("frontend")) return "🎨";
  if (r.includes("fullstack") || r.includes("full-stack")) return "🔧";
  if (r.includes("mobile"))   return "📱";
  if (r.includes("data") || r.includes("ml")) return "🧠";
  if (r.includes("devops") || r.includes("systems")) return "🛠️";
  return "💻";
}

function Disclosure({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-white/35 hover:text-white/60 transition-colors mt-2"
      >
        <svg
          className={`w-3 h-3 transition-transform ${open ? "rotate-90" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        {label}
      </button>
      {open && (
        <div className="mt-2 pl-4 border-l border-white/8 space-y-1">
          {children}
        </div>
      )}
    </div>
  );
}

function StatLine({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-baseline justify-between text-xs">
      <span className="text-white/35">{label}</span>
      <span className="text-white/60 font-mono">{value}</span>
    </div>
  );
}

function SpinnerIcon({ spinning }: { spinning: boolean }) {
  return (
    <svg
      className={`w-4 h-4 ${spinning ? "animate-spin" : ""}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
      />
    </svg>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function ProfileCard({ data, onReset, onRefresh }: ProfileCardProps) {
  const [copied,       setCopied]       = useState(false);
  const [refreshing,   setRefreshing]   = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [refreshedAt,  setRefreshedAt]  = useState<Date | null>(null);

  function copyShareLink() {
    const url = getShareUrl(data.username);
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  async function handleRefresh() {
    if (refreshing) return;
    setRefreshing(true);
    setRefreshError(null);
    try {
      await onRefresh();
      setRefreshedAt(new Date());
    } catch (err) {
      setRefreshError(err instanceof Error ? err.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  }

  const roleIcon = getRoleIcon(data.tech_focus.dominant_role);
  const overall  = data.overall_score.score;

  return (
    <div className="w-full max-w-2xl mx-auto space-y-3 animate-slide-up">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="card p-5 flex items-center gap-4">
        {data.avatar_url ? (
          <Image
            src={data.avatar_url}
            alt={data.username}
            width={56}
            height={56}
            className="rounded-full border-2 border-white/10"
          />
        ) : (
          <div className="w-14 h-14 rounded-full bg-white/10 flex items-center justify-center text-2xl">
            {roleIcon}
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-lg font-semibold text-white truncate">
              {data.name || `@${data.username}`}
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex-shrink-0">
              {data.recommendation.role_fit}
            </span>
            {data.cached && !refreshedAt && (
              <span className="text-xs text-white/25 border border-white/10 px-2 py-0.5 rounded-full flex-shrink-0">
                cached
              </span>
            )}
            {refreshedAt && (
              <span className="text-xs text-emerald-400/50 border border-emerald-500/20 px-2 py-0.5 rounded-full flex-shrink-0">
                updated {refreshedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            )}
          </div>
          <a
            href={`https://github.com/${data.username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-white/40 hover:text-emerald-400 font-mono transition-colors"
          >
            github.com/{data.username}
          </a>
        </div>

        {/* Overall score */}
        <div className="flex-shrink-0 text-center">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-emerald-400 font-mono leading-none">
              {overall.toFixed(1)}
            </span>
            <span className="text-[10px] text-white/30 mt-0.5">overall</span>
          </div>
        </div>
      </div>

      {/* ── Tech Focus ─────────────────────────────────────────────────────── */}
      <div className="card p-5">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-xl flex-shrink-0">
            {roleIcon}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-white/40 uppercase tracking-wider font-medium mb-1">Tech Focus</p>
            <p className="text-base font-semibold text-white">{data.tech_focus.label}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xs text-white/25">confidence</p>
            <p className="text-sm font-mono text-white/60">
              {Math.round(data.tech_focus.confidence * 100)}%
            </p>
          </div>
        </div>

        <Disclosure label="Language breakdown">
          {Object.entries(data.tech_focus.language_breakdown).map(([lang, pct]) => (
            <div key={lang} className="flex items-center gap-2">
              <div className="flex-1 h-1.5 rounded-full bg-white/8 overflow-hidden">
                <div
                  className="h-full rounded-full bg-emerald-500/60"
                  style={{ width: `${Math.min(pct, 100)}%` }}
                />
              </div>
              <span className="text-white/40 font-mono text-xs w-12 text-right">{lang}</span>
              <span className="text-white/25 font-mono text-xs w-10 text-right">{pct}%</span>
            </div>
          ))}
        </Disclosure>
      </div>

      {/* ── Performance Signals ────────────────────────────────────────────── */}
      <div className="card p-5 space-y-5">
        <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Performance Signals</p>

        <div>
          <ScoreBar label="Consistency" score={data.consistency.score} />
          <Disclosure label="Why this score?">
            <StatLine label="Active weeks (last 52)"    value={`${data.consistency.details.active_weeks} / 52`} />
            <StatLine label="Total commits"             value={data.consistency.details.total_commits} />
            <StatLine label="Avg commits / active week" value={data.consistency.details.avg_commits_per_active_week} />
            <StatLine label="Active weeks (last 12)"    value={`${data.consistency.details.recent_active_weeks} / 12`} />
            <StatLine label="Longest streak"            value={`${data.consistency.details.streak_weeks} weeks`} />
            <p className="text-xs text-white/40 italic mt-1">{data.consistency.details.comparison}</p>
          </Disclosure>
        </div>

        <div>
          <ScoreBar label="Project Complexity" score={data.project_complexity.score} />
          <Disclosure label="Why this score?">
            <StatLine label="README quality"        value={`${Math.round(data.project_complexity.details.readme_score * 100)}%`} />
            <StatLine label="Config files detected" value={data.project_complexity.details.config_file_count} />
            <StatLine label="Root directories"      value={data.project_complexity.details.directory_count} />
            <StatLine label="Engineering features"  value={data.project_complexity.details.features_detected.join(", ") || "None detected"} />
          </Disclosure>
        </div>

        <Disclosure label="Overall score formula  (0.4 × consistency + 0.4 × complexity + 0.2 × focus confidence)">
          <StatLine label="Consistency contribution" value={`${data.overall_score.consistency_contribution} pts`} />
          <StatLine label="Complexity contribution"  value={`${data.overall_score.complexity_contribution} pts`} />
          <StatLine label="Tech focus contribution"  value={`${data.overall_score.tech_focus_contribution} pts`} />
        </Disclosure>
      </div>

      {/* ── Top Project ────────────────────────────────────────────────────── */}
      <div className="card p-5 space-y-3">
        <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Top Project</p>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <a
              href={data.top_project.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-base font-semibold text-white hover:text-emerald-400 transition-colors font-mono"
            >
              {data.top_project.name}
            </a>
            {data.top_project.description && (
              <p className="text-sm text-white/50 mt-1 leading-relaxed">
                {data.top_project.description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 text-white/30 flex-shrink-0 text-sm">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
            </svg>
            <span className="font-mono text-xs">{data.top_project.stars}</span>
          </div>
        </div>
        {data.top_project.features.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {data.top_project.features.map((f) => (
              <TechBadge key={f} tech={f} />
            ))}
          </div>
        )}
      </div>

      {/* ── Missing Signals ────────────────────────────────────────────────── */}
      {data.missing_signals.length > 0 && (
        <div className="card p-5 space-y-3 border-amber-500/20 bg-amber-500/[0.03]">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <p className="text-xs text-amber-400/80 uppercase tracking-wider font-medium">Missing Signals</p>
          </div>
          <ul className="space-y-2">
            {data.missing_signals.map((signal, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-amber-200/60">
                <span className="mt-1.5 w-1 h-1 rounded-full bg-amber-500/50 flex-shrink-0" />
                {signal}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Recommendation ─────────────────────────────────────────────────── */}
      <div className="card p-5 space-y-4 border-emerald-500/20 bg-emerald-500/[0.03]">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <p className="text-xs text-emerald-400/70 uppercase tracking-wider font-medium">
            Recruiter Recommendation
          </p>
        </div>
        <p className="text-sm text-white/80 leading-relaxed">{data.recommendation.summary}</p>
        <div className="grid grid-cols-2 gap-3 pt-1">
          <div className="space-y-1.5">
            <p className="text-xs text-emerald-400/60 font-medium uppercase tracking-wider">Strengths</p>
            {data.recommendation.strengths.map((s, i) => (
              <div key={i} className="flex items-start gap-1.5 text-xs text-white/60">
                <span className="mt-1 w-1 h-1 rounded-full bg-emerald-500/60 flex-shrink-0" />
                {s}
              </div>
            ))}
          </div>
          <div className="space-y-1.5">
            <p className="text-xs text-red-400/60 font-medium uppercase tracking-wider">Areas to Probe</p>
            {data.recommendation.weaknesses.map((w, i) => (
              <div key={i} className="flex items-start gap-1.5 text-xs text-white/60">
                <span className="mt-1 w-1 h-1 rounded-full bg-red-500/60 flex-shrink-0" />
                {w}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Refresh error ──────────────────────────────────────────────────── */}
      {refreshError && (
        <div className="card px-4 py-3 border-red-500/20 bg-red-500/[0.03] flex items-center gap-3">
          <svg className="w-4 h-4 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-300/80 flex-1">{refreshError}</p>
          <button
            onClick={() => setRefreshError(null)}
            className="text-white/30 hover:text-white text-xs transition-colors"
          >
            dismiss
          </button>
        </div>
      )}

      {/* ── Actions ────────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        {/* Share */}
        <button
          onClick={copyShareLink}
          className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-white/10 hover:border-white/20 text-sm text-white/60 hover:text-white transition-all"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-emerald-400 text-xs">Copied!</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span className="text-xs">Share</span>
            </>
          )}
        </button>

        {/* Update */}
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          title="Re-fetch from GitHub and regenerate evaluation"
          className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-white/10 hover:border-emerald-500/30 text-sm text-white/60 hover:text-emerald-400 disabled:opacity-50 disabled:cursor-wait transition-all"
        >
          <SpinnerIcon spinning={refreshing} />
          <span className="text-xs">{refreshing ? "Updating…" : "Update"}</span>
        </button>

        {/* New search */}
        <button
          onClick={onReset}
          disabled={refreshing}
          className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl border border-white/10 hover:border-white/20 text-sm text-white/60 hover:text-white disabled:opacity-50 transition-all"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="text-xs">New</span>
        </button>
      </div>

      <p className="text-center text-xs text-white/15 pb-2">
        Update re-fetches live data from GitHub — bypasses cache
      </p>
    </div>
  );
}