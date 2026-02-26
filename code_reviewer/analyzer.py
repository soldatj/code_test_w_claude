"""File scanning and Claude-based analysis."""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def scan_python_files(directory: str) -> List[str]:
    """Scan directory recursively for Python files."""
    path = Path(directory)
    if not path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return sorted(
        str(f)
        for f in path.rglob("*.py")
        if "__pycache__" not in f.parts
    )


def analyze_file_with_claude(file_path: str) -> Dict[str, Any]:
    """Analyze a Python file by calling `claude --model sonnet -p`."""
    try:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
    except OSError as e:
        return _error_result(file_path, str(e))

    prompt = f"""Analyze the following Python file for code quality issues.

Please provide a structured analysis covering:
1. Bugs: logical errors, potential exceptions, incorrect behavior
2. Code Style: PEP 8 violations, naming conventions, readability issues
3. Performance: inefficient algorithms, unnecessary operations, memory issues
4. Security: potential vulnerabilities, unsafe operations, injection risks

For each category, list specific issues found. If no issues are found, use an empty list.

Respond ONLY with valid JSON in this exact format (no markdown fences):
{{
  "file": "{file_path}",
  "bugs": ["issue1", "issue2"],
  "code_style": ["issue1"],
  "performance": ["issue1"],
  "security": ["issue1"],
  "summary": "brief overall summary"
}}

File: {file_path}
Code:
{code}
"""

    try:
        result = subprocess.run(
            ["claude", "--model", "sonnet", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        return _error_result(file_path, "claude CLI not found — ensure it is installed and on PATH")
    except subprocess.TimeoutExpired:
        return _error_result(file_path, "Claude CLI timed out after 120 s")
    except Exception as e:
        return _error_result(file_path, str(e))

    if result.returncode != 0:
        return _error_result(file_path, result.stderr.strip() or "claude CLI exited with non-zero status")

    output = result.stdout.strip()
    return _parse_output(file_path, output)


def _parse_output(file_path: str, output: str) -> Dict[str, Any]:
    """Try to extract a JSON object from Claude's response."""
    # First attempt: direct parse
    try:
        data = json.loads(output)
        data["file"] = file_path
        return data
    except json.JSONDecodeError:
        pass

    # Second attempt: find first {...} block
    match = re.search(r"\{.*\}", output, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            data["file"] = file_path
            return data
        except json.JSONDecodeError:
            pass

    # Fallback: store raw output
    return {
        "file": file_path,
        "bugs": [],
        "code_style": [],
        "performance": [],
        "security": [],
        "summary": output[:500] if output else "No output received from Claude",
        "raw_output": output,
    }


def _error_result(file_path: str, error: str) -> Dict[str, Any]:
    return {
        "file": file_path,
        "error": error,
        "bugs": [],
        "code_style": [],
        "performance": [],
        "security": [],
        "summary": f"Analysis failed: {error}",
    }


def aggregate_analyses(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate all per-file analyses into a summary dict."""
    total_bugs: List[str] = []
    total_style: List[str] = []
    total_perf: List[str] = []
    total_sec: List[str] = []

    for a in analyses:
        total_bugs.extend(a.get("bugs", []))
        total_style.extend(a.get("code_style", []))
        total_perf.extend(a.get("performance", []))
        total_sec.extend(a.get("security", []))

    return {
        "total_files": len(analyses),
        "total_bugs": len(total_bugs),
        "total_style_issues": len(total_style),
        "total_performance_issues": len(total_perf),
        "total_security_issues": len(total_sec),
        "all_analyses": analyses,
    }


def generate_reports(aggregated: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """Write JSON and plain-text reports to *output_dir*."""
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, "review_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2, ensure_ascii=False)

    text_path = os.path.join(output_dir, "review_report.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        _write_text_report(f, aggregated)

    return {"json": json_path, "text": text_path}


def _write_text_report(f, aggregated: Dict[str, Any]) -> None:
    sep = "=" * 60
    thin = "-" * 40

    f.write(f"{sep}\n")
    f.write("CODE REVIEW REPORT\n")
    f.write(f"{sep}\n\n")
    f.write(f"Files analyzed    : {aggregated['total_files']}\n")
    f.write(f"Bugs              : {aggregated['total_bugs']}\n")
    f.write(f"Style issues      : {aggregated['total_style_issues']}\n")
    f.write(f"Performance issues: {aggregated['total_performance_issues']}\n")
    f.write(f"Security issues   : {aggregated['total_security_issues']}\n\n")

    f.write(f"{sep}\n")
    f.write("DETAILED ANALYSIS\n")
    f.write(f"{sep}\n\n")

    for analysis in aggregated["all_analyses"]:
        f.write(f"File: {analysis['file']}\n")
        f.write(f"{thin}\n")

        if "error" in analysis:
            f.write(f"ERROR: {analysis['error']}\n\n")
            continue

        f.write(f"Summary: {analysis.get('summary', 'N/A')}\n\n")

        for key, label in [
            ("bugs", "Bugs"),
            ("code_style", "Code Style"),
            ("performance", "Performance"),
            ("security", "Security"),
        ]:
            items = analysis.get(key, [])
            if items:
                f.write(f"{label}:\n")
                for item in items:
                    f.write(f"  - {item}\n")
                f.write("\n")

        f.write("\n")
