"""HTTP client for mapfan-agent-server API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator

import httpx
from httpx_sse import aconnect_sse
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    task_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    task_id: str
    origin: str


@dataclass
class MapfanClient:
    """HTTP client for the mapfan-agent API server."""

    api_url: str
    api_key: str = ""
    timeout: float = 120.0

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    @property
    def _base_url(self) -> str:
        return f"{self.api_url.rstrip('/')}/api/v1"

    async def health(self) -> bool:
        """Check if the API server is healthy."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self._base_url}/health", timeout=5.0)
                return resp.status_code == 200
            except httpx.ConnectError:
                return False

    async def chat(self, message: str, task_id: str | None = None) -> ChatResponse:
        """Send a message and get a complete response."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/chat",
                json=ChatRequest(message=message, task_id=task_id).model_dump(),
                headers=self._headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return ChatResponse(**resp.json())

    async def chat_stream(
        self, message: str, task_id: str | None = None
    ) -> AsyncIterator[tuple[str, str]]:
        """Send a message and stream the response as (event, data) tuples."""
        async with httpx.AsyncClient() as client:
            async with aconnect_sse(
                client,
                "POST",
                f"{self._base_url}/chat/stream",
                json=ChatRequest(message=message, task_id=task_id).model_dump(),
                headers=self._headers,
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            ) as event_source:
                async for event in event_source.aiter_sse():
                    yield (event.event, event.data)
