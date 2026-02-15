from src.reviewer.models import Severity, StyleComment
from src.rules.rule_loader import load_rules
from src.analysis.static_checks import CHECKERS
from src.llm.llm_reviewer import LLMReviewer
from src.llm.client import LLMClient


def should_send_to_llm(code: str, max_lines: int = 300) -> bool:
    return len(code.splitlines()) <= max_lines


def run_reviewer(file_path: str, code: str, enable_llm: bool = True, config_path: str = "config.yaml"):
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
        static_rules = load_rules("data/coding_standard/rules.yaml")
        for rule in static_rules:
            checker = CHECKERS.get(rule.id)
            if checker:
                comments.extend(checker(file_path, code, rule))
    except (FileNotFoundError, KeyError):
        # Static rules file doesn't exist or is misconfigured
        pass

    # LLM-based semantic review
    if enable_llm:
        try:
            llm_rules = load_rules("src/rules/llm_rules.yaml")
            llm_client = LLMClient(config_path=config_path)
            llm_reviewer = LLMReviewer(llm_client)

            if should_send_to_llm(code):
                comments.extend(llm_reviewer.review(file_path, code, llm_rules))
        except Exception as e:
            print(f"Warning: LLM review failed: {e}")

    if len(comments) == 0:
        comments.append(
            StyleComment(
                file_path=file_path,
                line_number=0,
                rule_id="NO_ISSUES",
                message="No violations found.",
                severity=Severity.INFO,
            )
        )

    return comments

    return comments