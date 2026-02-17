from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"


class Source(str, Enum):
    STATIC = "Static"
    LLM = "LLM"


@dataclass
class StyleComment:
    file_path: str
    line_number: int
    position: int
    rule_id: str
    message: str
    severity: Severity
    source: Source = Source.STATIC
