from src.reviewer.models import Severity, StyleComment
from src.rules.rule_loader import load_rules
from src.analysis.static_checks import CHECKERS


def run_reviewer(file_path: str, code: str):
    rules = load_rules("data/coding_standard/rules.yaml")

    all_comments = []

    for rule in rules:
        checker = CHECKERS.get(rule.id)
        if checker:
            all_comments.extend(checker(file_path, code, rule))
        

    if len(all_comments) == 0:
        all_comments.append(
            StyleComment(
                file_path=file_path,
                line_number=0,
                rule_id="NO_ISSUES",
                message="No violations found.",
                severity=Severity.INFO,
            )
        )
    return all_comments
