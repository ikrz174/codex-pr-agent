"""GitHub repository statistics and activity reporter."""

from typing import Optional, Dict, Any, List
import urllib.request
import json
import os


class RepoStats:
    """Pull live stats for a GitHub repository."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.api_url = "https://api.github.com"

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Codex-PR-Agent"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def _get(self, path: str) -> Any:
        req = urllib.request.Request(f"{self.api_url}{path}", headers=self._headers())
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_summary(self, repo: str) -> Dict[str, Any]:
        """Return a structured summary of a repository's activity."""
        info = self._get(f"/repos/{repo}")
        pulls_open = self._get(f"/repos/{repo}/pulls?state=open&per_page=1")
        issues_open = self._get(f"/repos/{repo}/issues?state=open&per_page=1&labels=bug")
        commits = self._get(f"/repos/{repo}/commits?per_page=5")

        recent_commits: List[Dict[str, str]] = []
        for c in commits:
            recent_commits.append({
                "sha": c["sha"][:7],
                "message": c["commit"]["message"].splitlines()[0],
                "author": c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"],
            })

        return {
            "repo": repo,
            "stars": info.get("stargazers_count", 0),
            "forks": info.get("forks_count", 0),
            "open_issues": info.get("open_issues_count", 0),
            "watchers": info.get("watchers_count", 0),
            "language": info.get("language"),
            "last_push": info.get("pushed_at"),
            "open_prs": len(pulls_open) if isinstance(pulls_open, list) else 0,
            "recent_commits": recent_commits,
        }
