import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reviewer.pipeline import run_reviewer


if __name__ == "__main__":
    path = sys.argv[1]

    with open(path, "r") as f:
        code = f.read()

    comments = run_reviewer(path, code)

    for c in comments:
        print(f"{c.file_path}:{c.line_number} [{c.severity}] [{c.source.value}] {c.message}")
