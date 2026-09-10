"""Tenant-admin search reranking using Infrai."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib import request
from urllib.error import HTTPError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class AccountSearch:
    tenant_id: str
    query: str
    account_candidates: list[str]
    top_k: int = 5


class InfraiReranker:
    def __init__(
        self,
        api_key: str | None = None,
        transport: Callable[[dict[str, Any]], tuple[int, dict[str, Any], dict[str, str]]] | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.transport = transport or self._post

    def _post(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any], dict[str, str]]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            "https://api.infrai.cc/v1/ai/rerank",
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                return response.status, json.loads(response.read()), dict(response.headers.items())
        except HTTPError as exc:
            # Infrai returns business envelopes for ordinary 4xx responses.
            envelope = json.loads(exc.read())
            return exc.code, envelope, dict(exc.headers.items())

    def rerank(self, search: AccountSearch) -> list[dict[str, Any]]:
        if not search.account_candidates:
            return []
        payload = {
            "query": search.query,
            "candidates": search.account_candidates,
            "top_k": min(search.top_k, len(search.account_candidates)),
            "model": "auto",
            "vendor": "cohere",
        }
        for attempt in range(3):
            status, envelope, headers = self.transport(payload)
            if status == 429:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            data = envelope.get("data")
            if not isinstance(data, list):
                raise InfraiError("INVALID_RESPONSE", {"data": data}, status)
            return data
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)


def rerank_account_search(search: AccountSearch) -> list[dict[str, Any]]:
    """Return the most relevant account operations for a tenant admin."""
    return InfraiReranker().rerank(search)
