import asyncio
from collections import defaultdict
from app.services.github import GitHubService
from app.services.scoring import (
    compute_consistency,
    compute_project_complexity_detailed,
    _tech_focus_impl as compute_tech_focus_full,
    detect_features,
    pick_top_repo,
    compute_missing_signals,
    compute_overall_score,
)
from app.services.ai_summary import generate_recommendation
from app.models.schemas import (
    ProfileResponse, TopProject,
    ConsistencyScore, ConsistencyDetails,
    ComplexityScore, ComplexityDetails,
    TechFocusDetail, OverallScoreBreakdown,
)


async def build_profile(username: str) -> ProfileResponse:
    gh = GitHubService()

    try:
        user_task  = asyncio.create_task(gh.get_user(username))
        repos_task = asyncio.create_task(gh.get_repos(username))
        user  = await user_task
        repos = await repos_task

        if not repos:
            raise ValueError(f"No public repositories found for @{username}")

        repos_sorted = sorted(
            repos,
            key=lambda r: (r.get("stargazers_count", 0) + (1 if r.get("updated_at") else 0)),
            reverse=True,
        )
        top_repos = repos_sorted[:10]

        # ── Commit activity ────────────────────────────────────────────────────
        activity_tasks = [gh.get_commit_activity(username, r["name"]) for r in top_repos[:5]]
        activities     = await asyncio.gather(*activity_tasks, return_exceptions=True)

        aggregated_weeks = [0] * 52
        for activity in activities:
            if isinstance(activity, list) and len(activity) >= 52:
                for i, count in enumerate(activity[-52:]):
                    aggregated_weeks[i] += count

        consistency_result = compute_consistency(aggregated_weeks)

        # ── Languages ──────────────────────────────────────────────────────────
        lang_tasks   = [gh.get_languages(username, r["name"]) for r in top_repos]
        lang_results = await asyncio.gather(*lang_tasks, return_exceptions=True)

        all_languages: dict[str, int] = defaultdict(int)
        for langs in lang_results:
            if isinstance(langs, dict):
                for lang, count in langs.items():
                    all_languages[lang] += count

        tech_result = compute_tech_focus_full(
            dict(all_languages), [r["name"] for r in top_repos]
        )

        # ── Repo complexity ────────────────────────────────────────────────────
        analysis_repos   = top_repos[:3]
        contents_tasks   = [gh.get_repo_contents(username, r["name"]) for r in analysis_repos]
        readme_tasks     = [gh.get_readme(username, r["name"]) for r in analysis_repos]
        contents_results = await asyncio.gather(*contents_tasks, return_exceptions=True)
        readme_results   = await asyncio.gather(*readme_tasks, return_exceptions=True)

        complexity_results = []
        repo_features: dict[str, list[str]] = {}

        for repo, contents, readme in zip(analysis_repos, contents_results, readme_results):
            safe_contents = contents if isinstance(contents, list) else []
            safe_readme   = readme if isinstance(readme, str) else ""
            result        = compute_project_complexity_detailed(repo, safe_contents, safe_readme)
            complexity_results.append(result)
            repo_features[repo["name"]] = result.details.features_detected

        avg_complexity = round(
            sum(r.score for r in complexity_results) / len(complexity_results)
            if complexity_results else 0.0, 1
        )

        # Aggregate all detected features across analyzed repos
        all_features: list[str] = []
        seen: set[str] = set()
        for feats in repo_features.values():
            for f in feats:
                if f not in seen:
                    all_features.append(f)
                    seen.add(f)

        # ── Missing signals ────────────────────────────────────────────────────
        missing = compute_missing_signals(
            consistency_result, complexity_results, all_features, len(repos)
        )

        # ── Overall score ──────────────────────────────────────────────────────
        overall = compute_overall_score(
            consistency_result, avg_complexity, tech_result.confidence
        )

        # ── Top project ────────────────────────────────────────────────────────
        complexity_scores = {
            r["name"]: complexity_results[i].score
            for i, r in enumerate(analysis_repos)
        }
        best_repo     = pick_top_repo(top_repos, complexity_scores)
        best_name     = best_repo.get("name", "")
        best_features = repo_features.get(best_name, all_features[:5])
        # Use the best complexity details if available, else first
        best_complexity_idx = next(
            (i for i, r in enumerate(analysis_repos) if r["name"] == best_name), 0
        )
        best_complexity_details = (
            complexity_results[best_complexity_idx].details if complexity_results else None
        )

        top_project = TopProject(
            name=best_name,
            description=best_repo.get("description"),
            url=best_repo.get("html_url", f"https://github.com/{username}/{best_name}"),
            features=best_features,
            stars=best_repo.get("stargazers_count", 0),
            language=best_repo.get("language"),
        )

        # ── Recommendation ─────────────────────────────────────────────────────
        recommendation = await generate_recommendation(
            username=username,
            tech_focus_label=tech_result.label,
            consistency_score=consistency_result.score,
            project_complexity=avg_complexity,
            top_project_name=best_name,
            features=all_features,
            missing_signals=missing,
            active_weeks=consistency_result.active_weeks,
            streak_weeks=consistency_result.streak_weeks,
        )

        # ── Assemble response ──────────────────────────────────────────────────
        return ProfileResponse(
            username=username,
            avatar_url=user.get("avatar_url"),
            name=user.get("name"),

            tech_focus=TechFocusDetail(
                label=tech_result.label,
                dominant_language=tech_result.dominant_language,
                dominant_role=tech_result.dominant_role,
                language_breakdown=tech_result.language_breakdown,
                confidence=tech_result.confidence,
            ),

            consistency=ConsistencyScore(
                score=consistency_result.score,
                details=ConsistencyDetails(
                    active_weeks=consistency_result.active_weeks,
                    total_commits=consistency_result.total_commits,
                    avg_commits_per_active_week=consistency_result.avg_commits_per_active_week,
                    recent_active_weeks=consistency_result.recent_active_weeks,
                    streak_weeks=consistency_result.streak_weeks,
                    comparison=consistency_result.comparison,
                ),
            ),

            project_complexity=ComplexityScore(
                score=avg_complexity,
                details=ComplexityDetails(
                    readme_score=best_complexity_details.readme_score if best_complexity_details else 0.0,
                    config_file_count=best_complexity_details.config_file_count if best_complexity_details else 0,
                    directory_count=best_complexity_details.directory_count if best_complexity_details else 0,
                    features_detected=all_features,
                    stars=best_complexity_details.stars if best_complexity_details else 0,
                ),
            ),

            overall_score=OverallScoreBreakdown(
                score=overall.score,
                consistency_contribution=overall.breakdown["consistency_contribution"],
                complexity_contribution=overall.breakdown["complexity_contribution"],
                tech_focus_contribution=overall.breakdown["tech_focus_contribution"],
            ),

            top_project=top_project,
            recommendation=recommendation,
            missing_signals=missing,
        )

    finally:
        await gh.close()

