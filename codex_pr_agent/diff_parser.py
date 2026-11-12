"""Diff parsing utilities for git patches and unified diffs."""

from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class DiffHunk:
    header: str
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: List[str] = field(default_factory=list)


@dataclass
class FileDiff:
    old_path: Optional[str]
    new_path: Optional[str]
    is_new: bool = False
    is_deleted: bool = False
    is_renamed: bool = False
    hunks: List[DiffHunk] = field(default_factory=list)

    @property
    def target_path(self) -> str:
        return self.new_path or self.old_path or "unknown"

    @property
    def additions(self) -> int:
        count = 0
        for hunk in self.hunks:
            count += sum(1 for line in hunk.lines if line.startswith("+") and not line.startswith("+++"))
        return count

    @property
    def deletions(self) -> int:
        count = 0
        for hunk in self.hunks:
            count += sum(1 for line in hunk.lines if line.startswith("-") and not line.startswith("---"))
        return count


def parse_unified_diff(diff_text: str) -> List[FileDiff]:
    """Parse a git unified diff string into structured FileDiff objects."""
    files: List[FileDiff] = []
    current_file: Optional[FileDiff] = None
    current_hunk: Optional[DiffHunk] = None

    lines = diff_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("diff --git"):
            if current_file:
                if current_hunk:
                    current_file.hunks.append(current_hunk)
                    current_hunk = None
                files.append(current_file)

            # Match: diff --git a/file b/file
            match = re.match(r"diff --git a/(.*?) b/(.*)", line)
            if match:
                current_file = FileDiff(old_path=match.group(1), new_path=match.group(2))
            else:
                current_file = FileDiff(old_path=None, new_path=None)

        elif current_file is not None:
            if line.startswith("new file mode"):
                current_file.is_new = True
            elif line.startswith("deleted file mode"):
                current_file.is_deleted = True
            elif line.startswith("rename from"):
                current_file.is_renamed = True
                current_file.old_path = line[12:].strip()
            elif line.startswith("rename to"):
                current_file.is_renamed = True
                current_file.new_path = line[10:].strip()
            elif line.startswith("--- "):
                path = line[4:].strip()
                if path.startswith("a/"):
                    current_file.old_path = path[2:]
            elif line.startswith("+++ "):
                path = line[4:].strip()
                if path.startswith("b/"):
                    current_file.new_path = path[2:]
            elif line.startswith("@@ "):
                if current_hunk:
                    current_file.hunks.append(current_hunk)

                # @@ -old_start,old_lines +new_start,new_lines @@
                hunk_match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", line)
                if hunk_match:
                    old_start = int(hunk_match.group(1))
                    old_lines = int(hunk_match.group(2) or 1)
                    new_start = int(hunk_match.group(3))
                    new_lines = int(hunk_match.group(4) or 1)
                    current_hunk = DiffHunk(
                        header=line,
                        old_start=old_start,
                        old_lines=old_lines,
                        new_start=new_start,
                        new_lines=new_lines,
                        lines=[]
                    )
                else:
                    current_hunk = DiffHunk(header=line, old_start=1, old_lines=0, new_start=1, new_lines=0)
            elif current_hunk is not None:
                current_hunk.lines.append(line)

        i += 1

    if current_file:
        if current_hunk:
            current_file.hunks.append(current_hunk)
        files.append(current_file)

    return files
