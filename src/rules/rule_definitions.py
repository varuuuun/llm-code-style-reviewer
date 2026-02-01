from dataclasses import dataclass
from src.reviewer.models import Severity


@dataclass
class Rule:
    id: str
    description: str
    applies_to: str
    severity: Severity
    message: str
