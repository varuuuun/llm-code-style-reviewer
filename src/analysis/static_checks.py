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
                    position=max_length + 1,
                    rule_id=rule.id,
                    message=rule.message,
                    severity=rule.severity,
                )
            )

    return comments

# ---------- Assignment Operator Spacing ----------
def check_operator_spacing(file_path: str, code: str, rule: Rule):
    comments = []
    
    # Matches: &&, ||, ==, !=, >=, <=, =, +=, -=, *=, /=, +, -, *, /, %, <, >
    operator_pattern = re.compile(
        r'(?P<op>&&|\|\||==|!=|>=|<=|[+\-*/%=<>]=?|[<>])'
    )

    for idx, line in enumerate(code.splitlines(), start=1):
        clean_line = line.split('//')[0].split('/*')[0]
        
        for match in operator_pattern.finditer(clean_line):
            op = match.group('op')
            start, end = match.span()
            
            # --- 1. Filter: Increment/Decrement (++, --) ---
            if op in '+-' and (
                (end < len(clean_line) and clean_line[end] == op) or 
                (start > 0 and clean_line[start-1] == op)
            ):
                continue
            
            # --- 2. Filter: Unary Minus (e.g., -5 or return -1) ---
            if op == '-' and (start == 0 or re.search(r'[=(,;]\s*$', clean_line[:start])):
                continue

            # --- 3. Filter: Generics Protection (e.g., List<String>) ---
            if op in '<>':
                # Check if touching an uppercase letter (Type name) or another bracket
                # Example: Map<String, Integer> or List<List<String>>
                touching_type = False
                if start > 0 and (clean_line[start-1].isupper() or clean_line[start-1] in '<>'):
                    touching_type = True
                if end < len(clean_line) and (clean_line[end].isupper() or clean_line[end] in '<>'):
                    touching_type = True
                
                if touching_type:
                    continue

            # --- 4. Spacing Check ---
            # Binary operators must have a space before AND after
            has_space_before = (start > 0 and clean_line[start-1] == ' ')
            has_space_after = (end < len(clean_line) and clean_line[end] == ' ')
            
            if not (has_space_before and has_space_after):
                comments.append(
                    StyleComment(
                        file_path=file_path,
                        line_number=idx,
                        position=start + 1,
                        rule_id=rule.id,
                        message=f"{rule.message} (Found '{op}')",
                        severity=rule.severity,
                    )
                )
                break # One warning per line is usually enough to avoid noise

    return comments

# ---------- IF spacing ----------
def check_if_spacing(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r'\bif\(')

    for i, line in enumerate(code.splitlines(), start=1):
        if pattern.search(line):
            comments.append(
                StyleComment(file_path, i, line.index("if(") + 1, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Comma spacing ----------
def check_comma_spacing(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r',[^\s]')

    for i, line in enumerate(code.splitlines(), start=1):
        if pattern.search(line):
            comments.append(
                StyleComment(file_path, i, line.index(",") + 1, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- Trailing whitespace ----------
def check_trailing_whitespace(file_path: str, code: str, rule: Rule):
    comments = []

    for i, line in enumerate(code.splitlines(), start=1):
        # 1. stripped_line removes all whitespace from both ends
        stripped_line = line.strip()
        
        # 2. Check if the line has actual code AND ends with whitespace
        # This ignores lines that are entirely whitespace (empty lines)
        if stripped_line and line.rstrip() != line:
            comments.append(
                StyleComment(file_path, i, len(line.rstrip()) + 1, rule.id, rule.message, rule.severity)
            )
    return comments

# ---------- Brace on same line ----------
def check_brace_same_line(file_path: str, code: str, rule: Rule):
    comments = []
    lines = code.splitlines()

    for i in range(len(lines) - 1):
        if lines[i].strip().endswith((")", "else")) and lines[i + 1].strip() == "{":
            comments.append(
                StyleComment(file_path, i + 2, 0, rule.id, rule.message, rule.severity)
            )
    return comments


# ---------- One statement per line ----------
def check_one_statement_per_line(file_path: str, code: str, rule: Rule):
    comments = []

    for i, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()

        if stripped.startswith("for") and "(" in stripped:
            continue

        if line.count(";") > 1:
            comments.append(
                StyleComment(file_path, i, line.index(";") + 1, rule.id, rule.message, rule.severity)
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
                StyleComment(file_path, i, 0, rule.id, rule.message, rule.severity)
            )

        if stripped.endswith("{"):
            indent_level += 1
    return comments

# ---------- Class naming ----------
def check_class_naming(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)')

    for i, line in enumerate(code.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            name = match.group(1)
            if not name[0].isupper() or "_" in name:
                comments.append(
                    StyleComment(file_path, i, match.start() + 1, rule.id, rule.message, rule.severity)
                )
    return comments


# ---------- Method naming ----------
def check_method_naming(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r'(public|private|protected)\s+[\w<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')

    for i, line in enumerate(code.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            name = match.group(2)
            if name[0].isupper() or "_" in name:
                comments.append(
                    StyleComment(file_path, i, match.start() + 1, rule.id, rule.message, rule.severity)
                )
    return comments


# ---------- Boolean variable naming ----------
def check_boolean_naming(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(r'\bboolean\s+([a-zA-Z_][a-zA-Z0-9_]*)')

    for i, line in enumerate(code.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            name = match.group(1)
            if not (name.startswith("is") or name.startswith("has")):
                comments.append(
                    StyleComment(file_path, i, match.start() + 1, rule.id, rule.message, rule.severity)
                )
    return comments

# ---------- Else on same line as closing brace ----------
def check_else_same_line(file_path, code, rule):
    comments = []
    lines = code.splitlines()

    for i in range(len(lines) - 1):
        if lines[i].strip() == "}" and lines[i + 1].strip().startswith("else"):
            comments.append(
                StyleComment(file_path, i + 2, 0, rule.id, rule.message, rule.severity)
            )
    return comments

# ---------- Empty block detection ----------
def check_empty_block(file_path, code, rule):
    comments = []
    lines = code.splitlines()

    for i in range(len(lines) - 1):
        if lines[i].strip().endswith("{") and lines[i + 1].strip() == "}":
            comments.append(
                StyleComment(file_path, i + 1, 0, rule.id, rule.message, rule.severity)
            )
    return comments

# ---------- Multiple variable declaration detection ----------
def check_multiple_var_declaration(file_path, code, rule):
    comments = []
    pattern = re.compile(r'\b(int|double|float|String|boolean|char)\s+\w+.*(,).*(?=;)')

    for i, line in enumerate(code.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            comments.append(
                StyleComment(file_path, i, match.start(2) + 1, rule.id, rule.message, rule.severity)
            )
    return comments

# ---------- Magic number detection ----------
def check_magic_numbers(file_path, code, rule):
    comments = []
    pattern = re.compile(r'(?<!\w)(-?\d+)(?!\w)')

    for i, line in enumerate(code.splitlines(), start=1):
        for match in pattern.findall(line):
            if match not in {"0", "1", "-1"}:
                comments.append(
                    StyleComment(file_path, i, match.start(), rule.id, rule.message, rule.severity)
                )
                break
    return comments

# ---------- Tabs used for indentation ----------
def check_tabs_used(file_path, code, rule):
    comments = []

    for i, line in enumerate(code.splitlines(), start=1):
        if "\t" in line:
            comments.append(
                StyleComment(file_path, i, line.index("\t"), rule.id, rule.message, rule.severity)
            )
    return comments

# ---------- Constant naming ----------
def check_constant_all_caps(file_path: str, code: str, rule: Rule):
    comments = []
    pattern = re.compile(
        r'\b(static\s+final|final\s+static)\s+[\w<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)'
    )

    for i, line in enumerate(code.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            name = match.group(2)
            if not name.isupper():
                comments.append(
                    StyleComment(file_path, i, match.start() + 1, rule.id, rule.message, rule.severity)
                )
    return comments

# ---------- Modifier order ----------
def check_modifier_order(file_path: str, code: str, rule: Rule):
    comments = []

    # Only care about lines with multiple modifiers
    modifier_pattern = re.compile(
        r'\b(public|protected|private)\b.*\b(abstract|static|final)\b|'
        r'\b(abstract)\b.*\b(static|final)\b|'
        r'\b(static)\b.*\b(final)\b'
    )

    bad_order_patterns = [
        re.compile(r'\b(static|final)\s+(public|protected|private)\b'),
        re.compile(r'\b(static)\s+(abstract)\b'),
        re.compile(r'\b(final)\s+(static)\b'),
    ]

    for i, line in enumerate(code.splitlines(), start=1):
        for pat in bad_order_patterns:
            match = pat.search(line)
            if match:
                comments.append(
                    StyleComment(file_path, i, match.start() + 1, rule.id, rule.message, rule.severity)
                )
                break

    return comments

# ---------- File end newline ----------
def check_file_end_newline(file_path: str, code: str, rule: Rule):
    comments = []

    if not code.endswith(("\n", "\r\n")):
        comments.append(
            StyleComment(
                file_path=file_path,
                line_number=len(code.splitlines()) + 1,
                position=0,
                rule_id=rule.id,
                message=rule.message,
                severity=rule.severity,
            )
        )

    return comments

# ---------- Imports order ----------
def check_imports_order(file_path: str, code: str, rule: Rule):
    comments = []
    lines = code.splitlines()

    imports = []
    import_lines = []

    for i, line in enumerate(lines, start=1):
        if line.startswith("import "):
            imports.append(line.strip())
            import_lines.append(i)

    if imports and imports != sorted(imports):
        comments.append(
            StyleComment(
                file_path=file_path,
                line_number=import_lines[0],
                position=0,
                rule_id=rule.id,
                message=rule.message,
                severity=rule.severity,
            )
        )

    return comments

CHECKERS = {
    "JAVA_LINE_LENGTH": check_line_length,
    "JAVA_OPERATOR_SPACING": check_operator_spacing,
    "JAVA_IF_SPACING": check_if_spacing,
    "JAVA_COMMA_SPACING": check_comma_spacing,
    "JAVA_TRAILING_WHITESPACE": check_trailing_whitespace,
    "JAVA_BRACE_SAME_LINE": check_brace_same_line,
    "JAVA_ONE_STATEMENT_PER_LINE": check_one_statement_per_line,
    "JAVA_INDENTATION": check_indentation,
    "JAVA_CLASS_NAMING": check_class_naming,
    "JAVA_METHOD_NAMING": check_method_naming,
    "JAVA_BOOLEAN_NAMING": check_boolean_naming,
    "JAVA_ELSE_SAME_LINE": check_else_same_line,
    "JAVA_EMPTY_BLOCK": check_empty_block,
    "JAVA_MULTIPLE_VAR_DECL": check_multiple_var_declaration,
    "JAVA_MAGIC_NUMBERS": check_magic_numbers,
    "JAVA_TABS_USED": check_tabs_used,
    "JAVA_CONSTANT_ALL_CAPS": check_constant_all_caps,
    "JAVA_MODIFIER_ORDER": check_modifier_order,
    "JAVA_FILE_END_NEWLINE": check_file_end_newline,
    "JAVA_IMPORTS_ORDER": check_imports_order
}