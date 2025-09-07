"""
LLM configuration for different providers
Choose your preferred LLM provider here
"""

import os
from dotenv import load_dotenv
load_dotenv()

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Options: ollama, openai, anthropic

def get_llm_config():
    """Get LLM configuration based on provider"""
    
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return {
            "class": ChatOpenAI,
            "model": "gpt-4o-mini",  # or gpt-4o for better quality
            "temperature": 0.7,
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return {
            "class": ChatAnthropic,
            "model": "claude-3-haiku-20240307",  # or claude-3-sonnet-20240229
            "temperature": 0.7,
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        }
    
    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return {
            "class": ChatOllama,
            "model": "gpt-oss:20b",
            "temperature": 0.7,
            "base_url": "http://localhost:11434"  # Ollama default port
        }
    
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

def create_llm(temperature=0.7):
    """Create an LLM instance with the configured provider"""
    config = get_llm_config()
    
    if LLM_PROVIDER == "openai":
        return config["class"](
            model=config["model"],
            temperature=temperature,
            api_key=config["api_key"]
        )
    
    elif LLM_PROVIDER == "anthropic":
        return config["class"](
            model=config["model"],
            temperature=temperature,
            api_key=config["api_key"]
        )
    
    elif LLM_PROVIDER == "ollama":
        return config["class"](
            model=config["model"],
            temperature=temperature,
            base_url=config["base_url"]
        )
