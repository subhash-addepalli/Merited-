from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.models.schemas import ProfileResponse, ProfileRequest
from app.models.profile import ProfileCache
from app.services.profile_builder import build_profile

router = APIRouter()

# Required keys that only exist in the new schema.
# If a cached row is missing any of these it is stale and must be rebuilt.
_NEW_SCHEMA_KEYS = {
    "username", "tech_focus", "consistency", "project_complexity",
    "overall_score", "top_project", "recommendation", "missing_signals",
}


def _cache_to_response(cached: ProfileCache) -> Optional[ProfileResponse]:
    """
    Re-hydrate a ProfileResponse from the cached JSON blob.
    Returns None when the row was written by an older schema version so the
    caller can transparently drop it and rebuild.
    """
    raw = cached.raw_data or {}
    if not _NEW_SCHEMA_KEYS.issubset(raw.keys()):
        return None
    try:
        return ProfileResponse.model_validate(raw)
    except Exception:
        return None


async def _store_profile(profile: ProfileResponse, db: AsyncSession) -> None:
    """Upsert a profile into the cache (delete-then-insert)."""
    await db.execute(
        delete(ProfileCache).where(ProfileCache.username == profile.username)
    )
    db.add(ProfileCache(
        username=profile.username,
        tech_focus=profile.tech_focus.label,
        consistency_score=profile.consistency.score,
        project_complexity=profile.project_complexity.score,
        top_project=profile.top_project.model_dump(),
        recommendation=profile.recommendation.summary,
        raw_data=profile.model_dump(),
    ))
    await db.commit()


async def _build_and_store(username: str, db: AsyncSession) -> ProfileResponse:
    """Run the full analysis pipeline and persist the result."""
    try:
        profile = await build_profile(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _raise_github_error(e, username)
    await _store_profile(profile, db)
    return profile


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/profile", response_model=ProfileResponse)
async def analyze_profile(
    request: ProfileRequest,
    db: AsyncSession = Depends(get_db),
):
    username = request.username.strip().lower()
    if not username or len(username) > 39:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")

    result = await db.execute(
        select(ProfileCache).where(ProfileCache.username == username)
    )
    cached = result.scalar_one_or_none()

    if cached:
        response = _cache_to_response(cached)
        if response is not None:
            response.cached = True
            return response
        # Stale schema — drop and rebuild silently
        await db.execute(
            delete(ProfileCache).where(ProfileCache.username == username)
        )
        await db.commit()

    return await _build_and_store(username, db)


@router.post("/profile/{username}/refresh", response_model=ProfileResponse)
async def refresh_profile(username: str, db: AsyncSession = Depends(get_db)):
    """Force a full re-analysis, bypassing the cache."""
    username = username.strip().lower()
    if not username or len(username) > 39:
        raise HTTPException(status_code=400, detail="Invalid GitHub username")
    return await _build_and_store(username, db)


@router.get("/profile/{username}", response_model=ProfileResponse)
async def get_profile(username: str, db: AsyncSession = Depends(get_db)):
    username = username.strip().lower()
    result = await db.execute(
        select(ProfileCache).where(ProfileCache.username == username)
    )
    cached = result.scalar_one_or_none()

    if not cached:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Submit via POST first.",
        )

    response = _cache_to_response(cached)
    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Cached profile is outdated. Submit via POST to regenerate.",
        )

    response.cached = True
    return response


# ── helpers ───────────────────────────────────────────────────────────────────

def _raise_github_error(exc: Exception, username: str) -> None:
    msg = str(exc)
    if "404" in msg or "Not Found" in msg:
        raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
    if "403" in msg or "rate limit" in msg.lower():
        raise HTTPException(
            status_code=429,
            detail="GitHub API rate limit reached. Add a GITHUB_TOKEN to .env to increase limits.",
        )
    raise HTTPException(status_code=500, detail="Failed to analyze profile. Please try again.")