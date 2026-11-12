"""Tests for reviewer."""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from codex_pr_agent.cli import main as cli_main
from codex_pr_agent.reviewer import CodeReviewer

SAMPLE_DIFF = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1,3 +1,4 @@
 def main():
+    print("Hello, world!")
     return 0
"""


class TestReviewer(unittest.TestCase):
    def test_offline_reviewer(self):
        reviewer = CodeReviewer(api_key=None)
        result = reviewer.review_diff(SAMPLE_DIFF, repo_name="test/repo", pr_title="Test PR")
        self.assertEqual(result.verdict, "COMMENT")
        self.assertEqual(result.total_additions, 1)
        self.assertEqual(result.total_deletions, 0)
        self.assertEqual(len(result.file_reviews), 1)
        self.assertIn("Offline Review", result.summary_markdown)

    def test_empty_diff(self):
        reviewer = CodeReviewer(api_key=None)
        result = reviewer.review_diff("", repo_name="test/repo", pr_title="Empty PR")
        self.assertEqual(result.verdict, "APPROVE")
        self.assertEqual(result.total_additions, 0)
        self.assertEqual(result.total_deletions, 0)
        self.assertEqual(len(result.file_reviews), 0)

    def test_cli_review_diff_json(self):
        buf = io.StringIO()
        orig_argv = sys.argv
        orig_stdin = sys.stdin
        try:
            sys.argv = ["codex-pr-agent", "review-diff", "-", "--json"]
            sys.stdin = io.StringIO(SAMPLE_DIFF)
            with redirect_stdout(buf):
                cli_main()
        finally:
            sys.argv = orig_argv
            sys.stdin = orig_stdin

        data = json.loads(buf.getvalue())
        self.assertEqual(data["verdict"], "COMMENT")
        self.assertEqual(data["total_additions"], 1)
        self.assertEqual(data["total_deletions"], 0)
        self.assertEqual(len(data["file_reviews"]), 1)


if __name__ == "__main__":
    unittest.main()
