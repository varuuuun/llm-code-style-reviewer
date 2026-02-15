import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reviewer.pipeline import run_reviewer


def severity_to_github_level(severity):
    """Convert severity to GitHub annotation level"""
    mapping = {
        "info": "notice",
        "minor": "warning",
        "major": "error",
    }
    return mapping.get(severity.value, "notice")


if __name__ == "__main__":
    path = sys.argv[1]

    with open(path, "r") as f:
        code = f.read()

    comments = run_reviewer(path, code)

    for c in comments:
        level = severity_to_github_level(c.severity)
        print(f"::{level} file={c.file_path},line={c.line_number}::{c.source.value} - {c.message}")
        
    if any(c.severity == "major" for c in comments):
        sys.exit(1)  # Exit with error code if there are major issues
