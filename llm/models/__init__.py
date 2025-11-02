"""Module des intégrations LLM"""
from .deepseek import DeepSeekLLM
from .huggingface import HuggingFaceLLM, HuggingFaceAPI

__all__ = ["DeepSeekLLM", "HuggingFaceLLM", "HuggingFaceAPI"]

