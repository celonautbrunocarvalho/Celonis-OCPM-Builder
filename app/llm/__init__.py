from app.llm.base import LLMBase, LLMResponse, ToolCall


def create_llm(provider: str, model: str, api_key: str, max_tokens: int) -> LLMBase:
    """Factory function to create the appropriate LLM adapter."""
    if provider == "anthropic":
        from app.llm.anthropic import AnthropicAdapter
        return AnthropicAdapter(model=model, api_key=api_key, max_tokens=max_tokens)
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Available providers: anthropic"
        )
