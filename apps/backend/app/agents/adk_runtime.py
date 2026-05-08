from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AdkRunRequest:
    agent_name: str
    state: dict[str, Any]


class AdkRuntime(Protocol):
    async def run(self, request: AdkRunRequest) -> dict[str, Any]:
        ...
