"""Abstract LLM interface. All provider adapters implement this contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """A single tool/function call requested by the LLM."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"  # "end_turn" | "tool_use"


class LLMBase(ABC):
    """Abstract base class for LLM adapters.

    Every provider adapter (Anthropic, OpenAI, Google, Ollama, etc.)
    must implement this interface. The rest of the app ONLY interacts
    with this interface — no provider-specific code leaks out.
    """

    @abstractmethod
    def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:
        """Send a conversation with tool definitions and get a response.

        Args:
            system_prompt: The system instruction for the assistant.
            messages: Conversation history as a list of dicts with keys:
                - role: "user" | "assistant" | "tool_result"
                - content: str or structured content
            tools: Tool definitions in a provider-agnostic format:
                [{"name": "...", "description": "...", "parameters": {...}}]

        Returns:
            LLMResponse with either text (end_turn) or tool_calls (tool_use).
        """
        ...
