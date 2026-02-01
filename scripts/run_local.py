import sys
from src.reviewer.pipeline import run_reviewer


if __name__ == "__main__":
    path = sys.argv[1]

    with open(path, "r") as f:
        code = f.read()

    comments = run_reviewer(path, code)

    for c in comments:
        print(f"{c.file_path}:{c.line_number} [{c.severity}] {c.message}")
