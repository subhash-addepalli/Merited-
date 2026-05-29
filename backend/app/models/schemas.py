from pydantic import BaseModel
from typing import Optional


class TopProject(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    features: list[str]
    stars: int = 0
    language: Optional[str] = None


# ── Explainability models ─────────────────────────────────────────────────────

class ConsistencyDetails(BaseModel):
    active_weeks: int
    total_commits: int
    avg_commits_per_active_week: float
    recent_active_weeks: int          # last 12 weeks
    streak_weeks: int
    comparison: str                   # heuristic peer comparison


class ConsistencyScore(BaseModel):
    score: float
    details: ConsistencyDetails


class ComplexityDetails(BaseModel):
    readme_score: float               # 0–1
    config_file_count: int
    directory_count: int
    features_detected: list[str]
    stars: int


class ComplexityScore(BaseModel):
    score: float
    details: ComplexityDetails


class TechFocusDetail(BaseModel):
    label: str
    dominant_language: str
    dominant_role: str
    language_breakdown: dict[str, float]   # lang → % of total bytes
    confidence: float                       # 0–1


class OverallScoreBreakdown(BaseModel):
    score: float
    consistency_contribution: float
    complexity_contribution: float
    tech_focus_contribution: float


# ── Structured recommendation ─────────────────────────────────────────────────

class Recommendation(BaseModel):
    summary: str          # full 2–3 line text
    strengths: list[str]  # 1–3 bullet points
    weaknesses: list[str] # 1–2 bullet points
    role_fit: str         # e.g. "Junior Backend Engineer"


# ── Top-level response ────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    username: str
    avatar_url: Optional[str] = None
    name: Optional[str] = None

    tech_focus: TechFocusDetail
    consistency: ConsistencyScore
    project_complexity: ComplexityScore
    overall_score: OverallScoreBreakdown

    top_project: TopProject
    recommendation: Recommendation
    missing_signals: list[str]

    cached: bool = False


class ProfileRequest(BaseModel):
    username: str

