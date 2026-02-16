from src.llm.prompts import LLM_REVIEW_PROMPT
from src.reviewer.models import StyleComment, Source
from src.llm.client import LLMClient
from src.rules.rule_definitions import Rule


class LLMReviewer:
    def __init__(self, client: LLMClient):
        self.client = client

    def _classify_issue(self, message: str) -> str:
        """
        Classify the issue to determine which rule it matches.
        Returns the appropriate rule ID based on the message content.
        """
        message_lower = message.lower()
        
        # Check for boolean/variable naming issues
        if any(word in message_lower for word in ["boolean", "flag", "variable name", "unclear", "descriptive"]):
            return "LLM_BOOLEAN_SEMANTICS"
        
        # Check for method doing too much
        if any(word in message_lower for word in ["more than one", "do too much", "single responsibility", "multiple"]):
            return "LLM_METHOD_SINGLE_RESPONSIBILITY"
        
        # Default to method name intent for other semantic issues
        return "LLM_METHOD_NAME_INTENT"

    def review(self, file_path: str, code: str, rules: list[Rule]) -> list[StyleComment]:
        comments = []

        prompt = LLM_REVIEW_PROMPT.strip()
        
        # Add line numbers to code for LLM clarity
        numbered_code = "\n".join(f"{i+1}: {line}" for i, line in enumerate(code.splitlines()))
        
        response = self.client.review(prompt, numbered_code)

        if response.strip() == "No issues found.":
            return comments

        for line in response.splitlines():
            if not line.startswith("Line"):
                continue

            try:
                prefix, message = line.split(":", 1)
                line_number = int(prefix.replace("Line", "").strip())
            except ValueError:
                continue

            # Classify the issue and find matching rule
            rule_id = self._classify_issue(message)
            matching_rule = next((r for r in rules if r.id == rule_id), None)
            
            if matching_rule:
                comments.append(
                    StyleComment(
                        file_path=file_path,
                        line_number=line_number,
                        rule_id=rule_id,
                        message=message.strip(),
                        severity=matching_rule.severity,
                        source=Source.LLM,
                    )
                )

        return comments
