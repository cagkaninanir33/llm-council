"""Command-line entry point for the LLM Council.

Usage (from project root):
    python council_cli.py "Your question"
    echo "Your question" | python council_cli.py --json
    python council_cli.py --file question.txt
"""

import argparse
import asyncio
import json
import sys

from backend.council import run_full_council


def main():
    parser = argparse.ArgumentParser(description="Run the 3-stage LLM Council.")
    parser.add_argument("question", nargs="?", help="Question (default: read stdin)")
    parser.add_argument("--file", help="Read the question from a file")
    parser.add_argument("--json", action="store_true", help="Print full result as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            question = f.read()
    else:
        question = args.question or sys.stdin.read()
    question = question.strip()
    if not question:
        parser.error("empty question")

    stage1, stage2, stage3, metadata = asyncio.run(run_full_council(question))

    if args.json:
        print(json.dumps(
            {"stage1": stage1, "stage2": stage2, "stage3": stage3, "metadata": metadata},
            ensure_ascii=False, indent=2,
        ))
        return

    print("## Final answer\n")
    print(stage3["response"])
    print("\n## Aggregate ranking (lower is better)\n")
    for r in metadata.get("aggregate_rankings", []):
        print(f"- {r['model']}: {r['average_rank']} ({r['rankings_count']} votes)")


if __name__ == "__main__":
    main()
