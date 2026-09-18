#!/usr/local/lib/hermes-agent/venv/bin/python
"""Profile-local MCP tools for public web research without paid search credentials."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from research_web import fetch_public_page, search_web


TOOL_NAMES = ("search_public_web", "fetch_public_source")

mcp = FastMCP(
    "research-web",
    instructions=(
        "Search public web results and retrieve public sources. Search snippets are discovery aids, "
        "not final evidence; fetch the underlying source before relying on it."
    ),
)


def tool_names() -> tuple[str, ...]:
    return TOOL_NAMES


@mcp.tool()
def search_public_web(query: str, limit: int = 10) -> list[dict[str, str]]:
    """Search the public web. Returns titles, URLs and discovery snippets.

    Open important results with fetch_public_source before citing them. Search
    snippets alone must not be treated as verified evidence.
    """
    return search_web(query, limit)


@mcp.tool()
def fetch_public_source(url: str, max_chars: int = 40000) -> dict[str, Any]:
    """Fetch and extract a public http(s) page or PDF while enforcing SSRF and robots protections."""
    return fetch_public_page(url, max_chars=max_chars)


if __name__ == "__main__":
    mcp.run(transport="stdio")
