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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.call_count = 0
    
    def call(self, prompt: str, code: str) -> str:
        """Call Gemini API"""
        self.call_count += 1
        print(f"[DEBUG] Gemini API Call #{self.call_count}")
        print(f"[DEBUG] URL: {self.base_url}/{self.model}:generateContent")
        print(f"[DEBUG] Prompt length: {len(prompt)} chars")
        print(f"[DEBUG] Code length: {len(code)} chars")
        
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"text": code},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            }
        }
        
        print(f"[DEBUG] Payload size: {len(str(payload))} chars")
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=30
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.HTTPError as e:
            print(f"[DEBUG] HTTP Error: {e.response.status_code}")
            response_text = e.response.text
            print(f"[DEBUG] Response text: {response_text[:500]}")
            
            # Parse 429 errors to show when quota resets
            if e.response.status_code == 429:
                try:
                    error_data = e.response.json()
                    message = error_data.get("error", {}).get("message", "")
                    
                    # Extract retry time from message like "Please retry in 35.235237901s"
                    retry_match = re.search(r'Please retry in ([\d.]+)s', message)
                    if retry_match:
                        retry_seconds = float(retry_match.group(1))
                        reset_time = datetime.now() + timedelta(seconds=retry_seconds)
                        print(f"\n⏰ QUOTA RESET TIME: {reset_time.strftime('%H:%M:%S')} (in {int(retry_seconds)} seconds)")
                        print(f"   Your free tier quota will reset at: {reset_time.isoformat()}\n")
                except (json.JSONDecodeError, ValueError, KeyError):
                    pass
            
            raise


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
    
    def call(self, prompt: str, code: str) -> str:
        """Call Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": prompt,
            "messages": [
                {"role": "user", "content": code}
            ],
            "temperature": self.temperature,
        }
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]


class LocalLLMProvider(BaseLLMProvider):
    """Local LLM server provider (Ollama, LM Studio, vLLM, etc.)"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:8000"
    
    def call(self, prompt: str, code: str) -> str:
        """Call local LLM server (OpenAI-compatible API)"""
        headers = {"Content-Type": "application/json"}
        
        # Assume OpenAI-compatible chat completion format
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
        
        # Try common endpoints for local servers
        endpoints = [
            f"{self.base_url}/v1/chat/completions",
            f"{self.base_url}/chat/completions",
            f"{self.base_url}/api/chat",
        ]
        
        last_error = None
        for endpoint in endpoints:
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats
                if "choices" in result:
                    return result["choices"][0]["message"]["content"]
                elif "message" in result:
                    return result["message"]
                else:
                    return str(result)
            except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
                last_error = e
                continue
        
        raise ConnectionError(
            f"Could not connect to local LLM at {self.base_url}. "
            f"Last error: {last_error}"
        )


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
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "local": LocalLLMProvider,
    }
    
    provider_name = config.provider.lower()
    if provider_name not in providers:
        raise ValueError(
            f"Unsupported provider: {provider_name}. "
            f"Supported providers: {list(providers.keys())}"
        )
    
    return providers[provider_name](config)
