"use client";
import { useEffect, useState } from "react";

interface ScoreBarProps {
  label: string;
  score: number; // 0–10
  color?: string;
}

function getScoreColor(score: number): string {
  if (score >= 7.5) return "bg-emerald-500";
  if (score >= 5) return "bg-amber-400";
  return "bg-red-400";
}

function getScoreLabel(score: number): string {
  if (score >= 8) return "Excellent";
  if (score >= 6.5) return "Strong";
  if (score >= 5) return "Moderate";
  if (score >= 3) return "Developing";
  return "Early Stage";
}

export function ScoreBar({ label, score, color }: ScoreBarProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 80);
    return () => clearTimeout(t);
  }, []);

  const pct = Math.min((score / 10) * 100, 100);
  const barColor = color || getScoreColor(score);
  const scoreLabel = getScoreLabel(score);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-white/60 font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/40">{scoreLabel}</span>
          <span className="text-sm font-semibold text-white font-mono">
            {score.toFixed(1)}
            <span className="text-white/30 text-xs">/10</span>
          </span>
        </div>
      </div>
      <div className="score-bar-track">
        <div
          className={`score-bar-fill ${barColor}`}
          style={{ width: mounted ? `${pct}%` : "0%" }}
        />
      </div>
    </div>
  );
}
