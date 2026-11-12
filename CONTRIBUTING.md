# Contributing to Codex PR Agent

Thank you for your interest in contributing to **Codex PR Agent**!

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/ikrz174/codex-pr-agent.git
   cd codex-pr-agent
   ```

2. Create a virtual environment and install in editable mode:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   pip install pytest
   ```

3. Run the test suite:
   ```bash
   pytest -v
   ```

## Pull Request Guidelines

- Ensure all new features include unit tests in the `tests/` directory.
- Keep external dependencies minimal (standard library preferred for network and parsing operations).
- Format commit messages cleanly: `feat: ...`, `fix: ...`, `docs: ...`.
- Open an issue for major architectural proposals before writing code.
