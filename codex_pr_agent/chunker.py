"""Token-aware diff chunker for large pull requests."""

from typing import List, Iterator
from .diff_parser import FileDiff


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for code."""
    return max(1, len(text) // 4)


def chunk_files(
    files: List[FileDiff],
    max_tokens_per_chunk: int = 3000
) -> Iterator[List[FileDiff]]:
    """
    Yield batches of FileDiff objects that fit within the token budget.

    Large individual files are yielded alone (oversized) to avoid silent truncation.
    """
    current_chunk: List[FileDiff] = []
    current_tokens = 0

    for file_diff in files:
        file_text = "\n".join("\n".join(h.lines) for h in file_diff.hunks)
        file_tokens = estimate_tokens(file_text)

        if current_chunk and current_tokens + file_tokens > max_tokens_per_chunk:
            yield current_chunk
            current_chunk = []
            current_tokens = 0

        current_chunk.append(file_diff)
        current_tokens += file_tokens

    if current_chunk:
        yield current_chunk


def smart_truncate(text: str, max_chars: int, ellipsis: str = "\n\n... [truncated]") -> str:
    """Truncate at the nearest newline boundary to avoid cutting mid-line."""
    if len(text) <= max_chars:
        return text
    cut = text.rfind("\n", 0, max_chars)
    if cut == -1:
        cut = max_chars
    return text[:cut] + ellipsis
