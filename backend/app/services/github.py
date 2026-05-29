import httpx
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from app.core.config import get_settings

settings = get_settings()

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Merited-App/1.0",
}
if settings.github_token:
    HEADERS["Authorization"] = f"Bearer {settings.github_token}"


class GitHubService:
    def __init__(self):
        self.base = settings.github_api_base
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=20.0)

    async def get_user(self, username: str) -> dict:
        resp = await self.client.get(f"{self.base}/users/{username}")
        resp.raise_for_status()
        return resp.json()

    async def get_repos(self, username: str) -> list[dict]:
        repos = []
        page = 1
        while True:
            resp = await self.client.get(
                f"{self.base}/users/{username}/repos",
                params={"per_page": 100, "page": page, "sort": "updated", "type": "owner"},
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        # Exclude forks
        return [r for r in repos if not r.get("fork", False)]

    async def get_commit_activity(self, username: str, repo_name: str) -> list[dict]:
        """Fetch weekly commit activity for a repo."""
        try:
            resp = await self.client.get(
                f"{self.base}/repos/{username}/{repo_name}/stats/participation"
            )
            if resp.status_code == 202:
                return []  # GitHub is computing, skip
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("owner", [])  # weekly commit counts, last 52 weeks
        except Exception:
            return []

    async def get_languages(self, username: str, repo_name: str) -> dict:
        try:
            resp = await self.client.get(
                f"{self.base}/repos/{username}/{repo_name}/languages"
            )
            if resp.status_code != 200:
                return {}
            return resp.json()
        except Exception:
            return {}

    async def get_repo_contents(self, username: str, repo_name: str) -> list[dict]:
        try:
            resp = await self.client.get(
                f"{self.base}/repos/{username}/{repo_name}/contents"
            )
            if resp.status_code != 200:
                return []
            return resp.json()
        except Exception:
            return []

    async def get_readme(self, username: str, repo_name: str) -> str:
        try:
            resp = await self.client.get(
                f"{self.base}/repos/{username}/{repo_name}/readme",
                headers={**HEADERS, "Accept": "application/vnd.github.raw"},
            )
            if resp.status_code != 200:
                return ""
            return resp.text[:5000]  # cap at 5k chars
        except Exception:
            return ""

    async def get_recent_commits(self, username: str) -> list[dict]:
        """Get commits by user in last 6 months across all repos."""
        since = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
        try:
            resp = await self.client.get(
                f"{self.base}/search/commits",
                params={
                    "q": f"author:{username} author-date:>{since}",
                    "per_page": 100,
                    "sort": "committer-date",
                },
                headers={**HEADERS, "Accept": "application/vnd.github.cloak-preview+json"},
            )
            if resp.status_code != 200:
                return []
            return resp.json().get("items", [])
        except Exception:
            return []

    async def close(self):
        await self.client.aclose()
