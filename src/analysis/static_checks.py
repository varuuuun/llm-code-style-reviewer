from src.reviewer.models import StyleComment
from src.rules.rule_definitions import Rule


def check_line_length(
    file_path: str,
    code: str,
    rule: Rule,
    max_length: int = 120,
) -> list[StyleComment]:
    comments = []

    for idx, line in enumerate(code.splitlines(), start=1):
        if len(line) > max_length:
            comments.append(
                StyleComment(
                    file_path=file_path,
                    line_number=idx,
                    rule_id=rule.id,
                    message=rule.message,
                    severity=rule.severity,
                )
            )

    return comments
