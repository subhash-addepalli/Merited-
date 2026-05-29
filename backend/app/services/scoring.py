from collections import defaultdict
import re
import math
from dataclasses import dataclass, field

# ── Language → role mapping ───────────────────────────────────────────────────
LANGUAGE_ROLES = {
    "Python": "Backend", "Go": "Backend", "Java": "Backend",
    "Ruby": "Backend", "PHP": "Backend", "Rust": "Backend",
    "C": "Systems", "C++": "Systems", "C#": "Backend",
    "JavaScript": "Frontend", "TypeScript": "Frontend",
    "HTML": "Frontend", "CSS": "Frontend", "Vue": "Frontend", "Svelte": "Frontend",
    "Dart": "Mobile", "Swift": "Mobile", "Kotlin": "Mobile",
    "Shell": "DevOps", "Dockerfile": "DevOps", "HCL": "DevOps",
    "Jupyter Notebook": "Data/ML", "R": "Data/ML",
}

FRAMEWORK_HINTS = {
    "react": "React", "next": "Next.js", "vue": "Vue", "angular": "Angular",
    "svelte": "Svelte", "django": "Django", "flask": "Flask",
    "fastapi": "FastAPI", "express": "Express", "rails": "Rails",
    "spring": "Spring", "laravel": "Laravel",
}

AUTH_KEYWORDS    = {"auth", "jwt", "oauth", "login", "token", "session", "passport", "authentication"}
DB_KEYWORDS      = {"db", "sql", "mongo", "postgres", "mysql", "sqlite", "redis", "database", "orm", "prisma", "sequelize", "mongoose"}
API_KEYWORDS     = {"api", "routes", "controller", "endpoint", "rest", "graphql", "handler", "router"}
TEST_KEYWORDS    = {"test", "spec", "jest", "pytest", "unittest", "vitest", "cypress", "playwright"}

CONFIG_FILES = {
    "requirements.txt", "pyproject.toml", "setup.py",
    "package.json", "yarn.lock", "pnpm-lock.yaml",
    "go.mod", "Cargo.toml", "pom.xml", "Gemfile",
    "Dockerfile", "docker-compose.yml", ".github",
    "Makefile", ".env.example",
}

# ── Result dataclasses ────────────────────────────────────────────────────────

@dataclass
class ConsistencyResult:
    score: float
    active_weeks: int          # out of last 52
    total_commits: int
    avg_commits_per_active_week: float
    recent_active_weeks: int   # last 12 weeks
    streak_weeks: int          # longest streak of consecutive active weeks
    comparison: str            # heuristic positioning vs peers


@dataclass
class ComplexityDetails:
    readme_score: float        # 0–1
    config_file_count: int
    directory_count: int
    features_detected: list[str]
    stars: int


@dataclass
class ComplexityResult:
    score: float
    details: ComplexityDetails


@dataclass
class TechFocusResult:
    label: str                 # e.g. "Backend (Python)"
    dominant_language: str
    dominant_role: str
    language_breakdown: dict[str, int]   # top-5 languages by byte share %
    confidence: float          # 0–1, how dominant the top role is


@dataclass
class OverallScore:
    score: float
    consistency_weight: float  # always 0.4
    complexity_weight: float   # always 0.4
    focus_weight: float        # always 0.2
    breakdown: dict


@dataclass
class MissingSignals:
    items: list[str]           # human-readable gaps


# ── Consistency ───────────────────────────────────────────────────────────────

def compute_consistency(weekly_commits: list[int]) -> ConsistencyResult:
    """
    Score 0–10 from 52-week commit participation.
    Returns rich details for explainability.
    """
    if not weekly_commits:
        return ConsistencyResult(
            score=0.0, active_weeks=0, total_commits=0,
            avg_commits_per_active_week=0.0, recent_active_weeks=0,
            streak_weeks=0, comparison="Insufficient data",
        )

    weeks = weekly_commits[-52:]
    active_weeks = sum(1 for w in weeks if w > 0)
    total_commits = sum(weeks)

    if total_commits == 0:
        return ConsistencyResult(
            score=0.0, active_weeks=0, total_commits=0,
            avg_commits_per_active_week=0.0, recent_active_weeks=0,
            streak_weeks=0, comparison="No public commits in the past year",
        )

    avg_per_active = round(total_commits / active_weeks, 1) if active_weeks else 0.0
    recent = weeks[-12:]
    recent_active = sum(1 for w in recent if w > 0)

    # Longest consecutive active-week streak
    streak = cur = 0
    for w in weeks:
        if w > 0:
            cur += 1
            streak = max(streak, cur)
        else:
            cur = 0

    activity_ratio  = active_weeks / len(weeks)
    volume_score    = min(math.log1p(total_commits) / math.log1p(200), 1.0)
    recency_ratio   = recent_active / 12

    raw = (activity_ratio * 0.4) + (volume_score * 0.35) + (recency_ratio * 0.25)
    score = round(min(raw * 10, 10.0), 1)

    # Heuristic comparison text
    if score >= 8.0:
        comparison = "More active than ~90% of public GitHub profiles"
    elif score >= 6.0:
        comparison = "More consistent than typical junior/bootcamp profiles"
    elif score >= 4.0:
        comparison = "Similar to average hobbyist contributor"
    elif score >= 2.0:
        comparison = "Less active than most job-seeking developers"
    else:
        comparison = "Very sparse public activity — may use private repos primarily"

    return ConsistencyResult(
        score=score,
        active_weeks=active_weeks,
        total_commits=total_commits,
        avg_commits_per_active_week=avg_per_active,
        recent_active_weeks=recent_active,
        streak_weeks=streak,
        comparison=comparison,
    )


# ── Tech focus ────────────────────────────────────────────────────────────────

def compute_tech_focus(all_languages: dict, repo_names: list[str]) -> TechFocusResult:
    if not all_languages:
        return TechFocusResult(
            label="General", dominant_language="Unknown",
            dominant_role="General", language_breakdown={}, confidence=0.0,
        )

    role_bytes: dict[str, int] = defaultdict(int)
    total_bytes = sum(all_languages.values()) or 1
    top_lang, top_bytes = "", 0

    for lang, b in all_languages.items():
        role_bytes[LANGUAGE_ROLES.get(lang, "General")] += b
        if b > top_bytes:
            top_bytes, top_lang = b, lang

    dominant_role = max(role_bytes, key=role_bytes.get)
    confidence = round(role_bytes[dominant_role] / total_bytes, 2)

    # Top-5 languages as percentage breakdown
    sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]
    breakdown = {lang: round(b / total_bytes * 100, 1) for lang, b in sorted_langs}

    # Framework hint from repo names
    all_text = " ".join(repo_names).lower()
    framework = next(
        (name for kw, name in FRAMEWORK_HINTS.items() if kw in all_text), ""
    )

    label = f"{dominant_role} ({framework or top_lang})"

    return TechFocusResult(
        label=label,
        dominant_language=top_lang,
        dominant_role=dominant_role,
        language_breakdown=breakdown,
        confidence=confidence,
    )


# ── README quality ────────────────────────────────────────────────────────────

def score_readme(readme: str) -> float:
    """0–1 score for README quality."""
    if not readme:
        return 0.0
    score = 0.0
    length = len(readme)
    if length > 2000:    score += 0.4
    elif length > 800:   score += 0.25
    elif length > 200:   score += 0.1
    headings = len(re.findall(r"^#{1,3}\s+\w+", readme, re.MULTILINE))
    score += min(headings * 0.08, 0.3)
    if "```" in readme:  score += 0.15
    if "shields.io" in readme or "badge" in readme.lower(): score += 0.1
    if re.search(r"(install|usage|getting started|setup)", readme, re.IGNORECASE):
        score += 0.05
    return min(score, 1.0)


# ── Feature detection ─────────────────────────────────────────────────────────

def detect_features(repo: dict, contents: list[dict], readme: str) -> list[str]:
    """Detect high-value engineering signals from repo artifacts."""
    name        = repo.get("name", "").lower()
    description = (repo.get("description") or "").lower()
    readme_low  = readme.lower()
    all_text    = f"{name} {description} {readme_low}"
    file_names  = {item["name"].lower() for item in contents if isinstance(item, dict)}

    features = []
    if any(kw in all_text for kw in AUTH_KEYWORDS) or \
       any(kw in fn for kw in AUTH_KEYWORDS for fn in file_names):
        features.append("Authentication")

    if any(kw in all_text for kw in DB_KEYWORDS) or \
       any(kw in fn for kw in DB_KEYWORDS for fn in file_names):
        features.append("Database Integration")

    if any(kw in all_text for kw in API_KEYWORDS):
        features.append("REST API")

    if "dockerfile" in file_names or "docker-compose.yml" in file_names:
        features.append("Docker")

    if ".github" in file_names:
        features.append("CI/CD")

    if any(kw in fn for kw in TEST_KEYWORDS for fn in file_names):
        features.append("Tests")

    return features[:6]


# ── Project complexity ────────────────────────────────────────────────────────

def compute_project_complexity_detailed(
    repo: dict, contents: list[dict], readme: str
) -> ComplexityResult:
    """
    Returns detailed breakdown alongside the 0–10 score.
    """
    readme_raw   = score_readme(readme)
    file_names   = {item["name"] for item in contents if isinstance(item, dict)}
    config_hits  = len(CONFIG_FILES.intersection(file_names))
    dir_count    = sum(1 for item in contents
                       if isinstance(item, dict) and item.get("type") == "dir")
    stars        = repo.get("stargazers_count", 0)
    features     = detect_features(repo, contents, readme)

    score  = readme_raw * 3
    score += min(config_hits * 0.5, 2.0)
    score += min(dir_count * 0.4, 2.0)
    score += min(math.log1p(stars) / math.log1p(50), 1.0)
    score += min(len(features) * 0.5, 2.0)

    return ComplexityResult(
        score=round(min(score, 10.0), 1),
        details=ComplexityDetails(
            readme_score=round(readme_raw, 2),
            config_file_count=config_hits,
            directory_count=dir_count,
            features_detected=features,
            stars=stars,
        ),
    )


# ── Missing signals ───────────────────────────────────────────────────────────

def compute_missing_signals(
    consistency: ConsistencyResult,
    complexity_results: list[ComplexityResult],
    all_features: list[str],
    total_repos: int,
) -> list[str]:
    """
    Return plain-English gaps that matter to a recruiter.
    Only flags what is genuinely absent — never punishes intentional choices.
    """
    gaps = []

    if consistency.active_weeks < 8:
        gaps.append("Low commit activity in the past year — hard to assess work rhythm")

    if consistency.streak_weeks < 3:
        gaps.append("No sustained streak of consistent contributions detected")

    if "Tests" not in all_features:
        gaps.append("No testing frameworks detected across analyzed repos")

    if "CI/CD" not in all_features:
        gaps.append("No CI/CD configuration found (.github/workflows)")

    if "Docker" not in all_features:
        gaps.append("No containerisation evidence (Dockerfile / docker-compose)")

    # Check README quality across repos
    avg_readme = (
        sum(r.details.readme_score for r in complexity_results) / len(complexity_results)
        if complexity_results else 0
    )
    if avg_readme < 0.25:
        gaps.append("README quality is low — projects are hard to evaluate at a glance")

    if total_repos < 3:
        gaps.append("Very few public repositories — limited signal for evaluation")

    # No large-scale project proxy: no repo has any stars + complex structure
    any_starred = any(r.details.stars > 0 for r in complexity_results)
    high_complexity = any(r.score >= 6.0 for r in complexity_results)
    if not any_starred and not high_complexity:
        gaps.append("No evidence of larger-scale or collaborative projects")

    return gaps


# ── Overall score ─────────────────────────────────────────────────────────────

def compute_overall_score(
    consistency: ConsistencyResult,
    avg_complexity: float,
    tech_confidence: float,
) -> OverallScore:
    """
    overall = 0.4 * consistency + 0.4 * complexity + 0.2 * (tech_confidence * 10)
    """
    c_contrib   = round(consistency.score * 0.4, 2)
    p_contrib   = round(avg_complexity * 0.4, 2)
    t_contrib   = round(tech_confidence * 10 * 0.2, 2)
    total       = round(min(c_contrib + p_contrib + t_contrib, 10.0), 1)

    return OverallScore(
        score=total,
        consistency_weight=0.4,
        complexity_weight=0.4,
        focus_weight=0.2,
        breakdown={
            "consistency_contribution": c_contrib,
            "complexity_contribution":  p_contrib,
            "tech_focus_contribution":  t_contrib,
        },
    )


# ── Repo selection ────────────────────────────────────────────────────────────

def pick_top_repo(repos: list[dict], complexity_scores: dict) -> dict:
    """Pick best repo by combined stars + complexity."""
    if not repos:
        return {}

    def repo_rank(repo):
        complexity = complexity_scores.get(repo["name"], 0)
        stars = repo.get("stargazers_count", 0)
        star_score = min(math.log1p(stars) / math.log1p(100), 1.0)
        return complexity * 0.7 + star_score * 10 * 0.3

    return max(repos, key=repo_rank)


# ── Legacy thin wrappers (keep existing callers happy) ────────────────────────

def compute_consistency_score(weekly_commits: list[int]) -> float:
    return compute_consistency(weekly_commits).score


def compute_tech_focus(all_languages: dict, repo_names: list[str]) -> str:
    return compute_tech_focus_full(all_languages, repo_names).label


def compute_tech_focus_full(all_languages: dict, repo_names: list[str]) -> TechFocusResult:
    # Rename to avoid shadowing within this module
    return _tech_focus_impl(all_languages, repo_names)


def _tech_focus_impl(all_languages: dict, repo_names: list[str]) -> TechFocusResult:
    if not all_languages:
        return TechFocusResult(
            label="General", dominant_language="Unknown",
            dominant_role="General", language_breakdown={}, confidence=0.0,
        )
    role_bytes: dict[str, int] = defaultdict(int)
    total_bytes = sum(all_languages.values()) or 1
    top_lang, top_bytes = "", 0
    for lang, b in all_languages.items():
        role_bytes[LANGUAGE_ROLES.get(lang, "General")] += b
        if b > top_bytes:
            top_bytes, top_lang = b, lang
    dominant_role = max(role_bytes, key=role_bytes.get)
    confidence = round(role_bytes[dominant_role] / total_bytes, 2)
    sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]
    breakdown = {lang: round(b / total_bytes * 100, 1) for lang, b in sorted_langs}
    all_text = " ".join(repo_names).lower()
    framework = next(
        (name for kw, name in FRAMEWORK_HINTS.items() if kw in all_text), ""
    )
    label = f"{dominant_role} ({framework or top_lang})"
    return TechFocusResult(
        label=label, dominant_language=top_lang, dominant_role=dominant_role,
        language_breakdown=breakdown, confidence=confidence,
    )


def compute_project_complexity(repo: dict, contents: list[dict], readme: str) -> float:
    return compute_project_complexity_detailed(repo, contents, readme).score
