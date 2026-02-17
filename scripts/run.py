import sys
import os
import requests

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reviewer.pipeline import run_reviewer
from src.reviewer.models import StyleComment


def severity_to_github_level(severity):
    """Convert severity to GitHub annotation level"""
    mapping = {
        "info": "notice",
        "minor": "warning",
        "major": "error",
    }
    return mapping.get(severity.value, "notice")

def format_comment_markdown(comment: StyleComment) -> str:
    # 1. Clean up the message (removing redundant prefixes if they exist)
    clean_msg = comment.message.replace("Warning: Static - ", "").replace("Warning: LLM - ", "")

    # 2. Assign Emojis based on Severity and Source
    if comment.rule_id == "NO_ISSUES":
        return f"### ✅ {comment.file_path}\n**All Clear!** No style violations found in this file."

    emoji = "💡"
    if comment.severity.value.upper() == "MAJOR":
        emoji = "🔴"
    elif comment.severity.value.upper() == "MINOR":
        emoji = "⚠️"
        
    source_label = "🤖 AI Analysis" if comment.source.value.upper() == "LLM" else "🔍 Static Check"

    # 3. Build a structured Markdown response
    return (
        f"### {emoji} {source_label} Suggestion\n"
        f"**Rule:** `{comment.rule_id}`\n\n"
        f"> {clean_msg}\n\n"
        f"---\n"
        f"*Found in {comment.file_path}*"
    )

def post_github_review(all_comments):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("GITHUB_EVENT_PATH") # You'll need to parse the PR number from the event JSON
    
    # Extract PR Number from the GitHub Event environment
    import json
    with open(os.getenv("GITHUB_EVENT_PATH"), 'r') as f:
        event_data = json.load(f)
        pr_number = event_data.get("number")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Format alerts for the GitHub API
    github_comments = []
    for c in all_comments:
        # Ensure line_number is at least 1
        ln = c.line_number if c.line_number > 0 else 1
        
        github_comments.append({
            "path": c.file_path,
            "line": ln,
            "body": format_comment_markdown(c),
            "side": "RIGHT" # This places the comment on the NEW version of the code
        })

    payload = {
        "event": "COMMENT", # Use "REQUEST_CHANGES" if severity is 'major'
        "body": "Code Style Review Summary: Please see the specific suggestions below.",
        "comments": github_comments
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        print(f"Failed to post review: {response.text}")


if __name__ == "__main__":
    path = sys.argv[1]
    print(f"Running reviewer on {path}")

    with open(path, "r") as f:
        code = f.read()

    comments = run_reviewer(path, code)

    post_github_review(comments)

    if any(c.severity == "major" for c in comments):
        sys.exit(1)  # Exit with error code if there are major issues
