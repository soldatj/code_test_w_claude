"""LangGraph StateGraph workflow for the code reviewer."""

from typing import Annotated, Any, Dict, List

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from code_reviewer.analyzer import (
    aggregate_analyses,
    analyze_file_with_claude,
    generate_reports,
    scan_python_files,
)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class CodeReviewState(TypedDict):
    directory: str
    output_dir: str
    files: List[str]
    current_file_index: int
    analyses: List[Dict[str, Any]]
    aggregated: Dict[str, Any]
    report_paths: Dict[str, str]
    errors: List[str]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def scan_files(state: CodeReviewState, config: RunnableConfig = None) -> CodeReviewState:
    """Scan the target directory and populate the file list."""
    print(f"[scan_files] Scanning: {state['directory']}")
    try:
        files = scan_python_files(state["directory"])
        print(f"[scan_files] Found {len(files)} Python file(s)")
        return {
            **state,
            "files": files,
            "current_file_index": 0,
            "analyses": [],
            "errors": [],
        }
    except Exception as e:
        print(f"[scan_files] Error: {e}")
        return {
            **state,
            "files": [],
            "current_file_index": 0,
            "analyses": [],
            "errors": [str(e)],
        }


def analyze_file(state: CodeReviewState, config: RunnableConfig = None) -> CodeReviewState:
    """Analyze the file at *current_file_index*."""
    files = state["files"]
    idx = state["current_file_index"]

    current_file = files[idx]
    total = len(files)
    print(f"[analyze_file] ({idx + 1}/{total}) {current_file}")

    analysis = analyze_file_with_claude(current_file)

    return {
        **state,
        "analyses": state["analyses"] + [analysis],
        "current_file_index": idx + 1,
    }


def aggregate_results(state: CodeReviewState, config: RunnableConfig = None) -> CodeReviewState:
    """Aggregate per-file analyses into a summary."""
    print(f"[aggregate_results] Aggregating {len(state['analyses'])} analysis result(s)")
    aggregated = aggregate_analyses(state["analyses"])
    return {**state, "aggregated": aggregated}


def generate_report(state: CodeReviewState, config: RunnableConfig = None) -> CodeReviewState:
    """Write JSON and text reports to the output directory."""
    print(f"[generate_report] Writing reports to: {state['output_dir']}")
    report_paths = generate_reports(state["aggregated"], state["output_dir"])
    return {**state, "report_paths": report_paths}


# ---------------------------------------------------------------------------
# Routing helpers
# ---------------------------------------------------------------------------

def _route_after_scan(state: CodeReviewState) -> str:
    return "analyze_file" if state["files"] else "aggregate_results"


def _route_after_analyze(state: CodeReviewState) -> str:
    if state["current_file_index"] < len(state["files"]):
        return "analyze_file"
    return "aggregate_results"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph():
    """Compile and return the code-review StateGraph."""
    g = StateGraph(CodeReviewState)

    g.add_node("scan_files", scan_files)
    g.add_node("analyze_file", analyze_file)
    g.add_node("aggregate_results", aggregate_results)
    g.add_node("generate_report", generate_report)

    g.add_edge(START, "scan_files")

    g.add_conditional_edges(
        "scan_files",
        _route_after_scan,
        {"analyze_file": "analyze_file", "aggregate_results": "aggregate_results"},
    )

    g.add_conditional_edges(
        "analyze_file",
        _route_after_analyze,
        {"analyze_file": "analyze_file", "aggregate_results": "aggregate_results"},
    )

    g.add_edge("aggregate_results", "generate_report")
    g.add_edge("generate_report", END)

    return g.compile()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_review(directory: str, output_dir: str = "review_output") -> CodeReviewState:
    """Run the full code-review workflow and return the final state."""
    app = build_graph()

    initial_state: CodeReviewState = {
        "directory": directory,
        "output_dir": output_dir,
        "files": [],
        "current_file_index": 0,
        "analyses": [],
        "aggregated": {},
        "report_paths": {},
        "errors": [],
    }

    return app.invoke(initial_state)
