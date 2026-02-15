from src.llm.config import load_config
from src.llm.providers import get_provider


class LLMClient:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize LLM client from config file.
        
        Args:
            config_path: Path to config.yaml file
        """
        self.config = load_config(config_path)
        self.provider = get_provider(self.config)

    def review(self, prompt: str, code: str) -> str:
        """
        Returns raw LLM text output.
        
        Args:
            prompt: System prompt with instructions
            code: Code snippet to review
            
        Returns:
            LLM response text
        """
        return self.provider.call(prompt, code)
