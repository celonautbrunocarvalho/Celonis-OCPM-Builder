"""Anthropic (Claude) LLM adapter."""

import json

import anthropic

from app.llm.base import LLMBase, LLMResponse, ToolCall


class AnthropicAdapter(LLMBase):
    """Adapter for the Anthropic Claude API."""

    def __init__(self, model: str, api_key: str, max_tokens: int):
        self.model = model
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic(api_key=api_key)

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert provider-agnostic tool definitions to Anthropic format."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"],
            }
            for tool in tools
        ]

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert provider-agnostic messages to Anthropic format."""
        anthropic_messages = []

        for msg in messages:
            role = msg["role"]

            if role == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": msg["content"],
                })

            elif role == "assistant":
                anthropic_messages.append({
                    "role": "assistant",
                    "content": msg["content"],
                })

            elif role == "tool_result":
                anthropic_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_use_id"],
                            "content": msg["content"],
                        }
                    ],
                })

        return anthropic_messages

    def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:
        """Send a conversation to Claude and return a normalized response."""
        anthropic_tools = self._convert_tools(tools) if tools else []
        anthropic_messages = self._convert_messages(messages)

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": anthropic_messages,
        }
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = self.client.messages.create(**kwargs)

        # Parse the response into our normalized format
        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        return LLMResponse(
            text="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls,
            stop_reason="tool_use" if response.stop_reason == "tool_use" else "end_turn",
        )
