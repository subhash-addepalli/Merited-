export interface TopProject {
  name: string;
  description: string | null;
  url: string;
  features: string[];
  stars: number;
  language: string | null;
}

export interface ConsistencyDetails {
  active_weeks: number;
  total_commits: number;
  avg_commits_per_active_week: number;
  recent_active_weeks: number;
  streak_weeks: number;
  comparison: string;
}

export interface ConsistencyScore {
  score: number;
  details: ConsistencyDetails;
}

export interface ComplexityDetails {
  readme_score: number;
  config_file_count: number;
  directory_count: number;
  features_detected: string[];
  stars: number;
}

export interface ComplexityScore {
  score: number;
  details: ComplexityDetails;
}

export interface TechFocusDetail {
  label: string;
  dominant_language: string;
  dominant_role: string;
  language_breakdown: Record<string, number>;
  confidence: number;
}

export interface OverallScoreBreakdown {
  score: number;
  consistency_contribution: number;
  complexity_contribution: number;
  tech_focus_contribution: number;
}

export interface Recommendation {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  role_fit: string;
}

export interface ProfileData {
  username: string;
  avatar_url: string | null;
  name: string | null;
  tech_focus: TechFocusDetail;
  consistency: ConsistencyScore;
  project_complexity: ComplexityScore;
  overall_score: OverallScoreBreakdown;
  top_project: TopProject;
  recommendation: Recommendation;
  missing_signals: string[];
  cached: boolean;
}

export type AppState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ProfileData }
  | { status: "error"; message: string };

