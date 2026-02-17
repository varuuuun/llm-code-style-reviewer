import os
import subprocess
import sys

BASE_BRANCH = os.getenv("BASE_BRANCH") or os.getenv("GITHUB_BASE_REF") or "main"

def get_changed_java_files():
    try:
        subprocess.run(["git", "fetch", "origin", BASE_BRANCH], check=True)

        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{BASE_BRANCH}...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )

        files = [
            f.strip()
            for f in result.stdout.splitlines()
            if f.endswith(".java")
        ]

        return files

    except Exception as e:
        print(f"Error detecting changed files: {e}")
        sys.exit(1)


def main():
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", "/github/workspace"],
        check=False
    )
    files = get_changed_java_files()

    if not files:
        print("No Java files changed.")
        sys.exit(0)

    exit_code = 0

    for file in files:
        print(f"Reviewing {file}")
        result = subprocess.run(
            ["python", "/action/scripts/run.py", file]
        )

        if result.returncode != 0:
            exit_code = result.returncode

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
