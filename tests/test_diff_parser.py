"""Tests for diff_parser."""

import unittest
from codex_pr_agent.diff_parser import parse_unified_diff

SAMPLE_DIFF = """diff --git a/src/auth.py b/src/auth.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/src/auth.py
@@ -0,0 +1,5 @@
+def verify_token(token: str) -> bool:
+    if not token:
+        return False
+    return token.startswith("secret_")
+
diff --git a/README.md b/README.md
index d8f19e2..b8a531f 100644
--- a/README.md
+++ b/README.md
@@ -10,3 +10,4 @@
 Existing line
-Old line to delete
+New replacement line
+Another added line
"""


class TestDiffParser(unittest.TestCase):
    def test_parse_sample_diff(self):
        files = parse_unified_diff(SAMPLE_DIFF)
        self.assertEqual(len(files), 2)

        auth_file = files[0]
        self.assertEqual(auth_file.target_path, "src/auth.py")
        self.assertTrue(auth_file.is_new)
        self.assertEqual(auth_file.additions, 5)
        self.assertEqual(auth_file.deletions, 0)

        readme = files[1]
        self.assertEqual(readme.target_path, "README.md")
        self.assertEqual(readme.additions, 2)
        self.assertEqual(readme.deletions, 1)

    def test_parse_empty_diff(self):
        files = parse_unified_diff("")
        self.assertEqual(len(files), 0)


if __name__ == "__main__":
    unittest.main()
