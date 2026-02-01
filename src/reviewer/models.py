from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"


@dataclass
class StyleComment:
    file_path: str
    line_number: int
    rule_id: str
    message: str
    severity: Severity
