"""Command-line interface for the code reviewer."""

import argparse
import os
import sys

from code_reviewer.graph import run_review


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code_reviewer",
        description="LangGraph-based Python code reviewer using Claude",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for Python files (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="review_output",
        metavar="DIR",
        help="Output directory for reports (default: review_output)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.", file=sys.stderr)
        return 1

    print("Code Reviewer")
    print("=" * 50)
    print(f"Directory : {directory}")
    print(f"Output    : {os.path.abspath(args.output)}")
    print()

    try:
        result = run_review(directory, args.output)
    except KeyboardInterrupt:
        print("\nReview cancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1

    # ---- summary ----
    errors = result.get("errors", [])
    if errors:
        print("\nErrors encountered during review:")
        for err in errors:
            print(f"  - {err}")

    aggregated = result.get("aggregated", {})
    report_paths = result.get("report_paths", {})

    print()
    print("Review complete!")
    print("-" * 50)
    print(f"Files analyzed    : {aggregated.get('total_files', 0)}")
    print(f"Bugs              : {aggregated.get('total_bugs', 0)}")
    print(f"Style issues      : {aggregated.get('total_style_issues', 0)}")
    print(f"Performance issues: {aggregated.get('total_performance_issues', 0)}")
    print(f"Security issues   : {aggregated.get('total_security_issues', 0)}")

    if report_paths:
        print()
        print("Reports:")
        print(f"  JSON : {report_paths.get('json')}")
        print(f"  Text : {report_paths.get('text')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
