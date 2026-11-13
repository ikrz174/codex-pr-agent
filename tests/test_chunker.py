"""Tests for chunker utilities."""

import unittest
from codex_pr_agent.chunker import estimate_tokens, smart_truncate, chunk_files
from codex_pr_agent.diff_parser import parse_unified_diff

SMALL_DIFF = """diff --git a/a.py b/a.py
index 1111111..2222222 100644
--- a/a.py
+++ b/a.py
@@ -1,2 +1,3 @@
 x = 1
+y = 2
 z = 3
"""

MULTI_DIFF = SMALL_DIFF + """diff --git a/b.py b/b.py
index 3333333..4444444 100644
--- a/b.py
+++ b/b.py
@@ -1,2 +1,3 @@
 a = 1
+b = 2
 c = 3
"""


class TestChunker(unittest.TestCase):
    def test_estimate_tokens(self):
        self.assertEqual(estimate_tokens(""), 1)
        self.assertEqual(estimate_tokens("x" * 100), 25)

    def test_smart_truncate_no_op(self):
        text = "hello world"
        self.assertEqual(smart_truncate(text, 100), text)

    def test_smart_truncate_cuts(self):
        text = "line one\nline two\nline three"
        result = smart_truncate(text, 15)
        self.assertIn("line one", result)
        self.assertIn("truncated", result)

    def test_chunk_files_single(self):
        files = parse_unified_diff(SMALL_DIFF)
        chunks = list(chunk_files(files, max_tokens_per_chunk=1000))
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 1)

    def test_chunk_files_split(self):
        files = parse_unified_diff(MULTI_DIFF)
        self.assertEqual(len(files), 2)
        # Force a very small budget to split into separate chunks
        chunks = list(chunk_files(files, max_tokens_per_chunk=1))
        self.assertEqual(len(chunks), 2)


if __name__ == "__main__":
    unittest.main()
