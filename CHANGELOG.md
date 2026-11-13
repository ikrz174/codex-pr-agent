# Changelog

All notable changes to **Codex PR Agent** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-13

### Added
- Token-aware diff chunker (`chunker.py`) with `chunk_files()` and `smart_truncate()` for large PR support.
- GitHub repository activity and stats reporter (`repo_stats.py`) for CI dashboards.
- `stats` CLI subcommand: print live star count, fork count, open issues, and recent commits for any public repo.
- 5 new unit tests covering chunker edge cases (empty budget, single file, multi-file split).

### Changed
- Bumped version to `0.2.0`.



### Added
- Initial release of `codex-pr-agent` CLI and GitHub Actions workflow.
- Unified git diff parser (`diff_parser.py`) with file stats and binary/ignore filtering.
- AI-powered code review & OWASP-aligned security audit prompts (`reviewer.py`, `prompts.py`).
- GitHub REST API client (`github_client.py`) using zero-dependency Python `urllib`.
- CLI subcommands: `review-pr`, `review-diff`, and `review-git`.
- `--format json|markdown` output option for CI/CD pipeline integration.
- Community governance files (`LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, issue templates).
