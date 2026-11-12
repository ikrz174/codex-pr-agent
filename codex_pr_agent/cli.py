"""Command-line interface for Codex PR Agent."""

import argparse
import subprocess
import sys
import os

from . import __version__
from .reviewer import CodeReviewer
from .github_client import GitHubClient


def run_git_diff(args: list) -> str:
    """Execute git diff command and return output."""
    try:
        res = subprocess.run(["git", "diff"] + args, capture_output=True, text=True, check=True)
        return res.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: git command not found.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="codex-pr-agent",
        description="Automated AI-powered Pull Request reviewer and security auditing tool."
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: review-pr
    pr_parser = subparsers.add_parser("review-pr", help="Review a remote GitHub Pull Request")
    pr_parser.add_argument("--repo", required=True, help="GitHub repository (e.g. owner/repo)")
    pr_parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    pr_parser.add_argument("--model", default="gpt-4o", help="OpenAI / LLM model name")
    pr_parser.add_argument("--post-comment", action="store_true", help="Post review comment directly to GitHub PR")
    pr_parser.add_argument("--submit-review", action="store_true", help="Submit official GitHub review verdict")

    # Command: review-diff
    diff_parser = subparsers.add_parser("review-diff", help="Review a local unified diff file")
    diff_parser.add_argument("file", help="Path to unified diff file (or - for stdin)")
    diff_parser.add_argument("--model", default="gpt-4o", help="OpenAI / LLM model name")

    # Command: review-git
    git_parser = subparsers.add_parser("review-git", help="Review local git changes directly")
    git_parser.add_argument("--staged", action="store_true", help="Review staged changes only (git diff --staged)")
    git_parser.add_argument("--base", default=None, help="Base branch/commit to diff against (e.g. main)")
    git_parser.add_argument("--model", default="gpt-4o", help="OpenAI / LLM model name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    reviewer = CodeReviewer(model=args.model)

    if args.command == "review-diff":
        if args.file == "-":
            diff_text = sys.stdin.read()
        else:
            with open(args.file, "r", encoding="utf-8") as f:
                diff_text = f.read()

        result = reviewer.review_diff(diff_text, repo_name="local-diff", pr_title=args.file)
        print(result.summary_markdown)

    elif args.command == "review-git":
        git_args = []
        if args.staged:
            git_args.append("--staged")
        elif args.base:
            git_args.append(args.base)

        diff_text = run_git_diff(git_args)
        if not diff_text.strip():
            print("No local git changes detected.")
            sys.exit(0)

        result = reviewer.review_diff(diff_text, repo_name="local-workspace", pr_title="Local Changes")
        print(result.summary_markdown)

    elif args.command == "review-pr":
        gh = GitHubClient()
        print(f"Fetching PR #{args.pr} from {args.repo}...")
        pr_info = gh.get_pr_info(args.repo, args.pr)
        pr_title = pr_info.get("title", f"PR #{args.pr}")
        diff_text = gh.get_pr_diff(args.repo, args.pr)

        print(f"Analyzing diff with model '{args.model}'...")
        result = reviewer.review_diff(diff_text, repo_name=args.repo, pr_title=pr_title)

        print("\n" + result.summary_markdown + "\n")

        if args.post_comment:
            print("Posting comment to GitHub...")
            gh.post_comment(args.repo, args.pr, result.summary_markdown)
            print("Comment posted successfully!")

        if args.submit_review:
            print(f"Submitting review verdict: {result.verdict}...")
            gh.submit_review(args.repo, args.pr, result.summary_markdown, event=result.verdict)
            print("Review submitted successfully!")


if __name__ == "__main__":
    main()
