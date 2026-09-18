"""Small, dependency-free client for the local Open Notebook API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


class OpenNotebookError(RuntimeError):
    """Base error returned by the Open Notebook bridge."""


class ApprovalRequired(OpenNotebookError):
    """Raised when a mutating operation lacks explicit human approval."""


class InvalidSourceURL(OpenNotebookError):
    """Raised when a suggested source URL is unsafe or unsupported."""


@dataclass(frozen=True)
class OpenNotebookClient:
    base_url: str
    password: str
    timeout: float = 30.0

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("OPEN_NOTEBOOK_URL must be an http(s) URL")
        if not self.password:
            raise ValueError("OPEN_NOTEBOOK_PASSWORD is required")
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = None
        headers = {
            "Authorization": f"Bearer {self.password}",
            "Accept": "application/json",
        }
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise OpenNotebookError(f"Open Notebook returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise OpenNotebookError(f"Cannot reach Open Notebook: {exc.reason}") from exc
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OpenNotebookError("Open Notebook returned invalid JSON") from exc

    def list_notebooks(self) -> list[dict[str, Any]]:
        result = self._request("GET", "/api/notebooks")
        if not isinstance(result, list):
            raise OpenNotebookError("Unexpected notebooks response")
        return result

    def create_notebook(self, name: str, description: str = "") -> dict[str, Any]:
        name = name.strip()
        if not name or len(name) > 200:
            raise ValueError("Notebook name must contain 1-200 characters")
        result = self._request(
            "POST",
            "/api/notebooks",
            {"name": name, "description": description.strip()[:2000]},
        )
        if not isinstance(result, dict):
            raise OpenNotebookError("Unexpected notebook creation response")
        return result

    @staticmethod
    def _validate_source_url(url: str) -> str:
        url = url.strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise InvalidSourceURL("Only absolute http(s) source URLs are allowed")
        if parsed.username or parsed.password:
            raise InvalidSourceURL("Source URLs must not contain credentials")
        if len(url) > 4096:
            raise InvalidSourceURL("Source URL is too long")
        return url

    @staticmethod
    def _require_approval(approved: bool) -> None:
        if approved is not True:
            raise ApprovalRequired(
                "Explicit user approval is required before adding anything to Open Notebook"
            )

    def add_source_url(
        self,
        notebook_id: str,
        url: str,
        *,
        title: str | None = None,
        approved: bool,
        embed: bool = False,
        async_processing: bool = True,
    ) -> dict[str, Any]:
        self._require_approval(approved)
        safe_url = self._validate_source_url(url)
        payload: dict[str, Any] = {
            "type": "link",
            "url": safe_url,
            "notebooks": [notebook_id],
            "embed": bool(embed),
            "async_processing": bool(async_processing),
        }
        if title and title.strip():
            payload["title"] = title.strip()[:500]
        result = self._request("POST", "/api/sources/json", payload)
        if not isinstance(result, dict):
            raise OpenNotebookError("Unexpected source creation response")
        return result

    def add_research_digest(
        self,
        notebook_id: str,
        title: str,
        content: str,
        source_urls: list[str],
        *,
        approved: bool,
        embed: bool = False,
        async_processing: bool = True,
    ) -> dict[str, Any]:
        self._require_approval(approved)
        if not content.strip():
            raise ValueError("Digest content is required")
        validated = [self._validate_source_url(url) for url in source_urls]
        citations = "\n".join(f"- {url}" for url in validated)
        full_content = content.strip()
        if citations:
            full_content += "\n\n## Fuentes\n" + citations
        payload = {
            "type": "text",
            "title": title.strip()[:500] or "Research digest",
            "content": full_content,
            "notebooks": [notebook_id],
            "embed": bool(embed),
            "async_processing": bool(async_processing),
        }
        result = self._request("POST", "/api/sources/json", payload)
        if not isinstance(result, dict):
            raise OpenNotebookError("Unexpected digest creation response")
        return result

    def get_source_status(self, source_id: str) -> dict[str, Any]:
        encoded = quote(source_id, safe="")
        result = self._request("GET", f"/api/sources/{encoded}/status")
        if not isinstance(result, dict):
            raise OpenNotebookError("Unexpected source status response")
        return result
