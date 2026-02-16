"""
Configuration loader for LLM settings.
Reads from config.yaml and provides a unified interface.
Supports environment variable overrides for CI/CD.
"""

import os
import yaml
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Unified LLM configuration"""
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


def load_config(config_path: str = "/action/config.yaml") -> LLMConfig:
    """
    Load LLM configuration from YAML file with environment variable overrides.
    
    Environment variables:
    - LLM_PROVIDER: Override provider (openai, gemini, claude, local)
    - {PROVIDER}_API_KEY: e.g., OPENAI_API_KEY, GEMINI_API_KEY, CLAUDE_API_KEY
    - {PROVIDER}_MODEL: e.g., OPENAI_MODEL, GEMINI_MODEL, etc.
    - {PROVIDER}_BASE_URL: For local LLM
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        LLMConfig object with the active provider's settings
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If provider not found in config or config is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    if not config_data:
        raise ValueError("Config file is empty")
    
    # Check for env var override of provider
    active_provider = os.getenv("LLM_PROVIDER", config_data.get("provider", "openai")).lower()
    
    if active_provider not in config_data:
        raise ValueError(f"Provider '{active_provider}' not found in config")
    
    provider_config = config_data[active_provider]
    
    # Build unified config from provider-specific settings
    # Environment variables override YAML
    provider_upper = active_provider.upper()
    
    llm_config = LLMConfig(
        provider=active_provider,
        model=os.getenv(f"{provider_upper}_MODEL", provider_config.get("model")),
        api_key=os.getenv(f"{provider_upper}_API_KEY", provider_config.get("api_key")),
        base_url=os.getenv(f"{provider_upper}_BASE_URL", provider_config.get("base_url")),
        temperature=float(os.getenv(f"{provider_upper}_TEMPERATURE", provider_config.get("temperature", 0.7))),
        max_tokens=int(os.getenv(f"{provider_upper}_MAX_TOKENS", provider_config.get("max_tokens", 1000))),
    )
    
    # Validate required fields
    if not llm_config.model:
        raise ValueError(f"Model not specified for provider '{active_provider}'")
    
    if active_provider in ["openai", "gemini", "claude"]:
        if not llm_config.api_key or "placeholder" in llm_config.api_key.lower():
            raise ValueError(
                f"API key not configured for {active_provider}. "
                f"Set environment variable {provider_upper}_API_KEY or update config.yaml"
            )
    
    return llm_config


def get_config() -> LLMConfig:
    """
    Convenience function to load config from default location.
    """
    return load_config()
