import httpx
import json
from app.core.config import get_settings
from app.models.schemas import Recommendation

settings = get_settings()


async def generate_recommendation(
    username: str,
    tech_focus_label: str,
    consistency_score: float,
    project_complexity: float,
    top_project_name: str,
    features: list[str],
    missing_signals: list[str],
    active_weeks: int,
    streak_weeks: int,
) -> Recommendation:
    """
    Generate a structured recruiter recommendation.
    Returns Recommendation(summary, strengths, weaknesses, role_fit).
    Falls back to deterministic if OpenAI unavailable.
    """
    if not settings.openai_api_key:
        return _fallback_recommendation(
            tech_focus_label, consistency_score, project_complexity,
            features, missing_signals,
        )

    feature_str  = ", ".join(features) if features else "no specific frameworks detected"
    missing_str  = "; ".join(missing_signals[:3]) if missing_signals else "none"

    prompt = f"""You are a senior engineering hiring manager writing a structured candidate evaluation.

Candidate GitHub data:
- Username: {username}
- Tech focus: {tech_focus_label}
- Consistency score: {consistency_score}/10  (active weeks: {active_weeks}/52, longest streak: {streak_weeks} weeks)
- Project complexity: {project_complexity}/10
- Top project: {top_project_name}
- Detected capabilities: {feature_str}
- Notable gaps: {missing_str}

Return a JSON object with exactly these keys:
{{
  "summary": "2–3 sentence plain-English evaluation a non-technical recruiter can read",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1"],
  "role_fit": "specific role title e.g. Junior Backend Engineer, Mid-level Full-Stack, etc."
}}

Rules:
- summary: direct, no filler, mentions tech focus + key signal + final verdict
- strengths: 1–3 items, specific and evidence-based (cite features or scores)
- weaknesses: 1–2 items, honest and actionable
- role_fit: single role title, no caveats

Return ONLY valid JSON. No markdown, no preamble."""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 250,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(raw)
            return Recommendation(
                summary=data.get("summary", ""),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                role_fit=data.get("role_fit", ""),
            )
    except Exception:
        return _fallback_recommendation(
            tech_focus_label, consistency_score, project_complexity,
            features, missing_signals,
        )


def _fallback_recommendation(
    tech_focus_label: str,
    consistency_score: float,
    project_complexity: float,
    features: list[str],
    missing_signals: list[str],
) -> Recommendation:
    """Deterministic structured recommendation — no external dependency."""

    role_type = tech_focus_label.split("(")[0].strip()

    # ── Strengths ──────────────────────────────────────────────────────────────
    strengths: list[str] = []
    if consistency_score >= 7:
        strengths.append("Consistent public commit history across the past year")
    elif consistency_score >= 4:
        strengths.append("Moderate commit activity with recent contributions")

    if features:
        strengths.append(f"Demonstrated experience with {', '.join(features[:3])}")

    if project_complexity >= 6:
        strengths.append("Projects show meaningful structural complexity and documentation")
    elif project_complexity >= 4:
        strengths.append("Projects cover core engineering fundamentals")

    if not strengths:
        strengths.append("Public GitHub presence with verifiable code samples")

    # ── Weaknesses ─────────────────────────────────────────────────────────────
    weaknesses: list[str] = []
    if consistency_score < 4:
        weaknesses.append("Sparse public activity makes work rhythm hard to assess")
    if "Tests" not in features:
        weaknesses.append("No testing evidence detected — unclear if quality practices are followed")
    if "CI/CD" not in features and not weaknesses:
        weaknesses.append("No CI/CD or automation signals in public repositories")
    if not weaknesses:
        weaknesses.append("Limited public signal — evaluation based on visible repos only")

    # ── Role fit ───────────────────────────────────────────────────────────────
    overall = consistency_score * 0.4 + project_complexity * 0.4
    if overall >= 6.5:
        seniority = "Mid-level"
    elif overall >= 4.0:
        seniority = "Junior"
    else:
        seniority = "Entry-level / Intern"

    role_fit = f"{seniority} {role_type} Engineer"

    # ── Summary ────────────────────────────────────────────────────────────────
    missing_note = ""
    if missing_signals:
        missing_note = f" Key gaps include: {missing_signals[0].lower()}."
    
    feature_sentence = (
        f"Demonstrates {', '.join(features[:2]).lower()} experience."
        if features
        else "Limited feature signals detected."
        )
    summary = (
        f"{role_type}-focused developer with a consistency score of {consistency_score}/10 "
        f"and project complexity of {project_complexity}/10. "
        f"{feature_sentence}"
        f"{missing_note} "
        f"Recommended for {role_fit.lower()} roles."
    )

    return Recommendation(
        summary=summary.strip(),
        strengths=strengths[:3],
        weaknesses=weaknesses[:2],
        role_fit=role_fit,
    )

