"""Core reviewer logic and multi-backend LLM integration."""

from dataclasses import dataclass
from typing import List, Optional
import os
import urllib.request
import json

from .diff_parser import FileDiff, parse_unified_diff
from .prompts import SYSTEM_PROMPT, DIFF_REVIEW_PROMPT, FULL_PR_SUMMARY_PROMPT


@dataclass
class ReviewResult:
    verdict: str  # APPROVE, REQUEST_CHANGES, COMMENT
    summary_markdown: str
    file_reviews: List[dict]
    total_additions: int
    total_deletions: int


class CodeReviewer:
    """Orchestrates AI code reviews for pull requests."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        max_file_diff_chars: int = 12000
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.max_file_diff_chars = max_file_diff_chars

    def _call_llm(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        """Execute chat completion request against OpenAI or compatible API."""
        if not self.api_key:
            # Deterministic fallback when no API key is set (e.g. offline CI / dry run)
            return (
                "### 🔍 Offline Review (No API Key Provided)\n\n"
                "- Diff parsed successfully.\n"
                "- Provide an `OPENAI_API_KEY` to run active AI model evaluations.\n\n"
                "**Verdict**: COMMENT"
            )

        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    def review_file(self, file_diff: FileDiff) -> dict:
        """Review a single modified file."""
        hunks_text = "\n".join("\n".join(h.lines) for h in file_diff.hunks)
        if len(hunks_text) > self.max_file_diff_chars:
            hunks_text = hunks_text[:self.max_file_diff_chars] + "\n\n... [diff truncated for length]"

        prompt = DIFF_REVIEW_PROMPT.format(
            file_path=file_diff.target_path,
            diff_content=hunks_text
        )

        feedback = self._call_llm(prompt)
        return {
            "file": file_diff.target_path,
            "additions": file_diff.additions,
            "deletions": file_diff.deletions,
            "feedback": feedback
        }

    def review_diff(
        self,
        diff_text: str,
        repo_name: str = "local-repo",
        pr_title: str = "Code Changes"
    ) -> ReviewResult:
        """Perform comprehensive review on a full diff text."""
        files = parse_unified_diff(diff_text)
        if not files:
            return ReviewResult(
                verdict="APPROVE",
                summary_markdown="No significant code diffs detected.",
                file_reviews=[],
                total_additions=0,
                total_deletions=0
            )

        total_additions = sum(f.additions for f in files)
        total_deletions = sum(f.deletions for f in files)

        file_reviews = []
        diff_summary_lines = []

        for f in files:
            fr = self.review_file(f)
            file_reviews.append(fr)
            diff_summary_lines.append(f"- `{f.target_path}` (+{f.additions}, -{f.deletions})")

        summary_prompt = FULL_PR_SUMMARY_PROMPT.format(
            repo_name=repo_name,
            pr_title=pr_title,
            file_count=len(files),
            additions=total_additions,
            deletions=total_deletions,
            diff_summary="\n".join(diff_summary_lines)
        )

        executive_summary = self._call_llm(summary_prompt)

        # Determine verdict
        verdict = "COMMENT"
        lower_summary = executive_summary.lower()
        if "request_changes" in lower_summary or "request changes" in lower_summary:
            verdict = "REQUEST_CHANGES"
        elif "approve" in lower_summary:
            verdict = "APPROVE"

        # Combine into complete report
        report_sections = [
            f"# 🤖 Codex PR Agent Review: {pr_title}",
            "",
            f"**Repository:** `{repo_name}` | **Files Changed:** {len(files)} (+{total_additions}/-{total_deletions})",
            f"**Verdict:** `{verdict}`",
            "",
            "## 📋 Executive Summary",
            executive_summary,
            "",
            "## 🔍 Detailed File Reviews"
        ]

        for fr in file_reviews:
            report_sections.extend([
                f"### 📄 `{fr['file']}` (+{fr['additions']}/-{fr['deletions']})",
                fr["feedback"],
                ""
            ])

        return ReviewResult(
            verdict=verdict,
            summary_markdown="\n".join(report_sections),
            file_reviews=file_reviews,
            total_additions=total_additions,
            total_deletions=total_deletions
        )
