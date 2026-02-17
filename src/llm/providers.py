"""
LLM Provider implementations.
Supports: OpenAI, Gemini, Claude, and local LLM servers.
"""

from abc import ABC, abstractmethod
import json
import re
from datetime import datetime, timedelta
from typing import Optional
import requests
from src.llm.config import LLMConfig


class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
    
    @abstractmethod
    def call(self, prompt: str, code: str) -> str:
        """
        Make a request to the LLM.
        
        Args:
            prompt: System prompt/instructions
            code: Code snippet to review
            
        Returns:
            LLM response text
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (including Azure OpenAI compatible endpoints)"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.openai.com/v1"
    
    def call(self, prompt: str, code: str) -> str:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Prepare messages for chat completion
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": code},
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]

def get_provider(config: LLMConfig) -> BaseLLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        config: LLM configuration
        
    Returns:
        Instantiated provider based on config.provider
        
    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "openai": OpenAIProvider
    }
    
    provider_name = config.provider.lower()
    if provider_name not in providers:
        raise ValueError(
            f"Unsupported provider: {provider_name}. "
            f"Supported providers: {list(providers.keys())}"
        )
    
    return providers[provider_name](config)
