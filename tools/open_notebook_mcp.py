#!/usr/local/lib/hermes-agent/venv/bin/python
"""Profile-local MCP bridge from Hermes to Open Notebook."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP

from open_notebook_client import OpenNotebookClient


TOOL_NAMES = (
    "list_notebooks",
    "create_research_notebook",
    "add_source_url",
    "add_research_digest",
    "get_source_status",
)

mcp = FastMCP(
    "open-notebook",
    instructions=(
        "Read and write the local Open Notebook instance. Mutating tools require "
        "approved=true and must only be called after explicit human approval."
    ),
)


def tool_names() -> tuple[str, ...]:
    return TOOL_NAMES


def make_client(env_path: str | None = None) -> OpenNotebookClient:
    if env_path is None:
        hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        env_file = hermes_home / ".env"
    else:
        env_file = Path(env_path)
    file_values = dotenv_values(env_file) if env_file.is_file() else {}
    password = os.environ.get("OPEN_NOTEBOOK_PASSWORD") or file_values.get("OPEN_NOTEBOOK_PASSWORD") or ""
    if not password:
        raise RuntimeError("OPEN_NOTEBOOK_PASSWORD is not configured for this profile")
    base_url = (
        os.environ.get("OPEN_NOTEBOOK_URL")
        or file_values.get("OPEN_NOTEBOOK_URL")
        or "http://127.0.0.1:8502"
    )
    return OpenNotebookClient(str(base_url), str(password))


@mcp.tool()
def list_notebooks() -> list[dict[str, Any]]:
    """List Open Notebook notebooks and their IDs before proposing a target."""
    return make_client().list_notebooks()


@mcp.tool()
def create_research_notebook(
    name: str = "Deep Research — Hermes",
    description: str = "Investigaciones verificadas, fuentes y digestiones creadas por notebookllm.",
) -> dict[str, Any]:
    """Create a dedicated research notebook. Creating it is an external mutation."""
    return make_client().create_notebook(name, description)


@mcp.tool()
def add_source_url(
    notebook_id: str,
    url: str,
    approved: bool,
    title: str | None = None,
    embed: bool = False,
) -> dict[str, Any]:
    """Add one approved http(s) source URL to a selected notebook.

    Set approved=true only after the user explicitly accepted that exact source
    and notebook destination in the current conversation.
    """
    return make_client().add_source_url(
        notebook_id,
        url,
        title=title,
        approved=approved,
        embed=embed,
        async_processing=True,
    )


@mcp.tool()
def add_research_digest(
    notebook_id: str,
    title: str,
    content: str,
    source_urls: list[str],
    approved: bool,
    embed: bool = False,
) -> dict[str, Any]:
    """Add an approved research digest with its source URLs as a text source.

    Set approved=true only after the user reviewed the proposed digest and
    explicitly approved adding it to the specified notebook.
    """
    return make_client().add_research_digest(
        notebook_id,
        title,
        content,
        source_urls,
        approved=approved,
        embed=embed,
        async_processing=True,
    )


@mcp.tool()
def get_source_status(source_id: str) -> dict[str, Any]:
    """Read the current asynchronous processing status of a source."""
    return make_client().get_source_status(source_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
