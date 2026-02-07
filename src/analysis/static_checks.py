import re
from src.reviewer.models import StyleComment
from src.rules.rule_definitions import Rule

# ---------- Line Length ----------
def check_line_length(file_path: str, code: str, rule: Rule, max_length: int = 120):
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

# ---------- Assignment Operator Spacing ----------
def check_assignment_operator_spacing(file_path: str, code: str, rule: Rule):
    comments = []

    pattern = re.compile(r'(?<![=!<>+\-*/])=(?![=])')

    for idx, line in enumerate(code.splitlines(), start=1):
        if pattern.search(line):
            if " = " not in line:
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

# ---------- IF spacing ----------
def check_if_spacing(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r'\bif\(')

    for i, line in enumerate(code.splitlines(), start=1):
        if pattern.search(line):
            comments.append(
                StyleComment(file_path, i, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Comma spacing ----------
def check_comma_spacing(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r',[^\s]')

    for i, line in enumerate(code.splitlines(), start=1):
        if pattern.search(line):
            comments.append(
                StyleComment(file_path, i, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Trailing whitespace ----------
def check_trailing_whitespace(file_path: str, code: str, rule: Rule):
    comments = []

    for i, line in enumerate(code.splitlines(), start=1):
        if line.rstrip() != line:
            comments.append(
                StyleComment(file_path, i, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Brace on same line ----------
def check_brace_same_line(file_path: str, code: str, rule: Rule):
    comments = []
    lines = code.splitlines()

    for i in range(len(lines) - 1):
        if lines[i].strip().endswith((")", "else")) and lines[i + 1].strip() == "{":
            comments.append(
                StyleComment(file_path, i + 2, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- One statement per line ----------
def check_one_statement_per_line(file_path: str, code: str, rule: Rule):
    comments = []

    for i, line in enumerate(code.splitlines(), start=1):
        if line.count(";") > 1:
            comments.append(
                StyleComment(file_path, i, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Indentation ----------
def check_indentation(file_path: str, code: str, rule: Rule):
    comments = []
    indent_level = 0

    for i, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()

        if stripped.startswith("}"):
            indent_level = max(indent_level - 1, 0)

        if stripped and not line.startswith(" " * (indent_level * 4)):
            comments.append(
                StyleComment(file_path, i, rule.id, rule.message, rule.severity)
            )

        if stripped.endswith("{"):
            indent_level += 1

    return comments

CHECKERS = {
    "JAVA_LINE_LENGTH": check_line_length,
    "JAVA_OPERATOR_SPACING_ASSIGNMENT": check_assignment_operator_spacing,
    "JAVA_IF_SPACING": check_if_spacing,
    "JAVA_COMMA_SPACING": check_comma_spacing,
    "JAVA_TRAILING_WHITESPACE": check_trailing_whitespace,
    "JAVA_BRACE_SAME_LINE": check_brace_same_line,
    "JAVA_ONE_STATEMENT_PER_LINE": check_one_statement_per_line,
    "JAVA_INDENTATION": check_indentation,
}