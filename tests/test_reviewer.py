"""Tests for reviewer."""

import unittest
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


if __name__ == "__main__":
    unittest.main()
