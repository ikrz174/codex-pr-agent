<div align="center">

# 🤖 Codex PR Agent

**Autonomous AI-Powered Pull Request Reviewer & Security Auditing CLI for Open-Source Maintainers**

[![CI Tests](https://github.com/ikrz174/codex-pr-agent/actions/workflows/test.yml/badge.svg)](https://github.com/ikrz174/codex-pr-agent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Powered by: OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI%20Codex-412991.svg)](https://openai.com)

</div>

---

## 📖 Overview

**Codex PR Agent** is a lightweight, zero-bloat CLI tool and GitHub Action designed to alleviate maintainer burnout on open-source repositories. It automatically parses git diffs, analyzes architectural changes, audits potential security vulnerabilities, and generates structured, constructive code reviews directly on GitHub pull requests.

Built specifically for maintainers stewarding high-velocity open-source ecosystems.

---

## ✨ Features

- 🛡️ **Automated Security Auditing:** Flags OWASP Top 10 vulnerabilities, credential leaks, unvalidated inputs, and auth bypass patterns before code hits production.
- 🎯 **Constructive & Surgical Feedback:** Categorizes suggestions into `🚨 CRITICAL`, `⚠️ WARNING`, and `💡 SUGGESTION` with actionable code snippets.
- ⚡ **Local & CI Workflows:** Run locally on staged git changes prior to push, or deploy as a GitHub Action on every PR.
- 🤖 **Multi-Model Integration:** Seamlessly supports OpenAI Codex / GPT-4o, OpenAI-compatible backends, and offline fallback mode.
- 📦 **Zero Heavy Dependencies:** Written entirely in pure modern Python using standard library networking to guarantee zero supply-chain overhead.

---

## 🚀 Quickstart

### 1. Installation

Install via pip directly from GitHub or local source:

```bash
git clone https://github.com/ikrz174/codex-pr-agent.git
cd codex-pr-agent
pip install -e .
```

### 2. Environment Configuration

Export your OpenAI API token (or any OpenAI-compatible API key):

```bash
export OPENAI_API_KEY="sk-..."
# Optional: customize model or API base
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

---

## 💻 CLI Usage

### Review Local Unstaged/Staged Git Changes
Audit your local changes before creating a pull request:

```bash
# Review staged git changes
codex-pr-agent review-git --staged

# Review changes compared to main branch
codex-pr-agent review-git --base main
```

### Review a Remote GitHub Pull Request
Fetch, analyze, and post reviews directly to a GitHub PR:

```bash
export GITHUB_TOKEN="ghp_..."

codex-pr-agent review-pr \
  --repo "owner/repository" \
  --pr 42 \
  --model "gpt-4o" \
  --post-comment \
  --submit-review
```

### Review a Diff File
Analyze an exported unified patch or diff file:

```bash
git diff > changes.patch
codex-pr-agent review-diff changes.patch
```

---

## ⚙️ GitHub Actions Integration

Automate code reviews for incoming pull requests by adding `.github/workflows/ai-review.yml` to your repository:

```yaml
name: AI Pull Request Review

on:
  pull_request_target:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Codex PR Agent
        run: pip install git+https://github.com/ikrz174/codex-pr-agent.git
      - name: Execute Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codex-pr-agent review-pr \
            --repo "${{ github.repository }}" \
            --pr "${{ github.event.pull_request.number }}" \
            --model "gpt-4o" \
            --post-comment \
            --submit-review
```

---

## 🧪 Testing

Run the test suite with pytest:

```bash
pytest -v
```

---

## 🤝 Contributing

Contributions and feedback are welcome! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on development and submitting pull requests.

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).
