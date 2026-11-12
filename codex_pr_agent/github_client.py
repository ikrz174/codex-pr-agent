"""GitHub API client for pull requests and review comments."""

from typing import Optional, Dict, Any
import os
import urllib.request
import json


class GitHubClient:
    """Interacts with GitHub REST API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.api_url = "https://api.github.com"

    def _headers(self, accept: str = "application/vnd.github.v3+json") -> Dict[str, str]:
        headers = {
            "Accept": accept,
            "User-Agent": "Codex-PR-Agent"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """Fetch the unified diff of a pull request."""
        url = f"{self.api_url}/repos/{repo}/pulls/{pr_number}"
        req = urllib.request.Request(
            url,
            headers=self._headers(accept="application/vnd.github.v3.diff")
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")

    def get_pr_info(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch pull request metadata."""
        url = f"{self.api_url}/repos/{repo}/pulls/{pr_number}"
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def post_comment(self, repo: str, pr_number: int, body: str) -> Dict[str, Any]:
        """Post a review comment to the pull request discussion."""
        url = f"{self.api_url}/repos/{repo}/issues/{pr_number}/comments"
        payload = {"body": body}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers()
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def submit_review(self, repo: str, pr_number: int, body: str, event: str = "COMMENT") -> Dict[str, Any]:
        """Submit an official GitHub Pull Request Review."""
        url = f"{self.api_url}/repos/{repo}/pulls/{pr_number}/reviews"
        payload = {
            "body": body,
            "event": event  # APPROVE, REQUEST_CHANGES, COMMENT
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers()
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
