from src.reviewer.models import Severity, StyleComment
from src.rules.rule_loader import load_rules
from src.analysis.static_checks import CHECKERS
from src.llm.llm_reviewer import LLMReviewer
from src.llm.client import LLMClient


def should_send_to_llm(code: str, max_lines: int = 300) -> bool:
    return len(code.splitlines()) <= max_lines


def run_reviewer(file_path: str, code: str, enable_llm: bool = True, config_path: str = "/action/config.yaml"):
    """
    Run the code reviewer (static checks + optional LLM review).
    
    Args:
        file_path: Path to the code file
        code: Code content to review
        enable_llm: Whether to enable LLM-based reviews
        config_path: Path to LLM config file
        
    Returns:
        List of StyleComment objects
    """
    comments = []

    # Try static rules if they exist
    try:
        static_rules = load_rules("/action/data/coding_standard/rules.yaml")
        for rule in static_rules:
            checker = CHECKERS.get(rule.id)
            if checker:
                comments.extend(checker(file_path, code, rule))
    except (Exception) as e:
        # Static rules file doesn't exist or is misconfigured
        print(f"Warning: Static rule checks failed: {e}")

    # LLM-based semantic review
    if enable_llm:
        try:
            llm_rules = load_rules("/action/src/rules/llm_rules.yaml")
            llm_client = LLMClient(config_path=config_path)
            llm_reviewer = LLMReviewer(llm_client)

            if should_send_to_llm(code):
                comments.extend(llm_reviewer.review(file_path, code, llm_rules))
        except Exception as e:
            print(f"Warning: LLM review failed: {e}")

    commented_lines = {}
    commented_line = False
    lines = code.splitlines()
    for line in range(len(lines)):
        print(str(line) + ": " + lines[line])
        if lines[line].find("//") != -1:
            commented_lines[line+1] = [lines[line].index("//"), len(lines[line])]
        elif lines[line].find("/*") != -1:
            if lines[line].find("*/") != -1:
                commented_lines[line+1] = [lines[line].index("/*"), lines[line].index("*/") + 2]
            else:
                commented_lines[line+1] = [lines[line].index("/*"), len(lines[line])]
                commented_line = True
        elif commented_line and lines[line].find("*/") != -1:
            commented_lines[line+1] = [0, lines[line].index("*/") + 2]
            commented_line = False
        elif commented_line:
            commented_lines[line+1] = [0, len(lines[line])]

    to_ignore = []
    for i in range(len(comments)):
        if comments[i].line_number in commented_lines:
            comment_start, comment_end = commented_lines[comments[i].line_number]
            if comment_start <= comments[i].position <= comment_end:
                to_ignore.append(i)
    
    print(to_ignore)
    for i in sorted(to_ignore, reverse=True):
        del comments[i]

    if len(comments) == 0:
        comments.append(
            StyleComment(
                file_path=file_path,
                line_number=1,
                position=0,
                rule_id="NO_ISSUES",
                message="No violations found.",
                severity=Severity.INFO,
            )
        )

    return comments

