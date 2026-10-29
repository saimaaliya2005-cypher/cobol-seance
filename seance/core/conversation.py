"""Conversation manager — maintains chat history per spirit session."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # "user" or "assistant"
    content: str


class Conversation:
    """Manages the conversation history for a séance session.

    Keeps a rolling window of messages to stay within context limits
    while preserving the spirit's personality continuity.
    """

    def __init__(self, max_history: int = 20):
        """Initialize conversation.

        Args:
            max_history: Maximum number of messages to retain.
        """
        self._messages: list[Message] = []
        self._max_history = max_history

    def add_user_message(self, content: str) -> None:
        """Record a user message."""
        self._messages.append(Message(role="user", content=content))
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Record a spirit (assistant) response."""
        self._messages.append(Message(role="assistant", content=content))
        self._trim()

    def to_messages_list(self) -> list[dict[str, str]]:
        """Convert to the format expected by the Ollama API.

        Returns:
            List of {"role": ..., "content": ...} dicts.
        """
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def clear(self) -> None:
        """Clear all conversation history."""
        self._messages.clear()

    def message_count(self) -> int:
        """Return the number of messages in history."""
        return len(self._messages)

    def last_assistant_message(self) -> str | None:
        """Return the last assistant message content, if any."""
        for msg in reversed(self._messages):
            if msg.role == "assistant":
                return msg.content
        return None

    def _trim(self) -> None:
        """Trim history to max_history, keeping the most recent messages."""
        if len(self._messages) > self._max_history:
            # Always keep at least the first exchange (greeting) for personality continuity
            keep_first = 2  # First user prompt + first assistant response
            overflow = len(self._messages) - self._max_history
            if overflow > 0 and len(self._messages) > keep_first:
                # Keep first exchange + trim from middle
                first = self._messages[:keep_first]
                recent = self._messages[keep_first + overflow:]
                self._messages = first + recent
