import yaml
from src.rules.rule_definitions import Rule
from src.reviewer.models import Severity


def load_rules(path: str) -> list[Rule]:
    with open(path, "r") as f:
        raw_rules = yaml.safe_load(f)

    rules = []
    for r in raw_rules:
        rules.append(
            Rule(
                id=r["id"],
                description=r["description"],
                applies_to=r["applies_to"],
                severity=Severity(r["severity"]),
                message=r["message"],
            )
        )
    return rules
