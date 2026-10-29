"""Async client for communicating with Ollama's local LLM API."""

from __future__ import annotations

from typing import AsyncIterator

import httpx


class OllamaClient:
    """Handles streaming chat completions from a local Ollama instance."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "gemma3:4b"):
        self.host = host.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(base_url=self.host, timeout=120.0)

    async def check_connection(self) -> bool:
        """Check if Ollama is running and reachable."""
        try:
            resp = await self._client.get("/api/tags")
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    async def check_model_available(self) -> bool:
        """Check if the configured model is pulled and ready."""
        try:
            resp = await self._client.get("/api/tags")
            if resp.status_code != 200:
                return False
            data = resp.json()
            model_names = [m.get("name", "") for m in data.get("models", [])]
            # Check both exact match and base name match (e.g. "gemma3:4b" matches "gemma3:4b")
            base_model = self.model.split(":")[0]
            return any(
                self.model in name or base_model in name for name in model_names
            )
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    async def list_models(self) -> list[str]:
        """List all locally available models."""
        try:
            resp = await self._client.get("/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "unknown") for m in data.get("models", [])]
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        return []

    async def stream_chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        """Stream a chat completion token-by-token.

        Args:
            system_prompt: The spirit's persona/system prompt.
            messages: Conversation history as [{"role": "user"|"assistant", "content": "..."}].

        Yields:
            Individual text tokens as they arrive from the model.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            "stream": True,
            "options": {
                "temperature": 0.85,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_predict": 512,
            },
        }

        async with self._client.stream(
            "POST", "/api/chat", json=payload
        ) as response:
            import json

            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        return
                except json.JSONDecodeError:
                    continue

    async def generate_single(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        """Non-streaming chat completion. Returns the full response at once."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            "stream": False,
            "options": {
                "temperature": 0.85,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "num_predict": 512,
            },
        }

        resp = await self._client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
