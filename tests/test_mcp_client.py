"""Integration checks against the hosted Meridian MCP server (requires network)."""

from __future__ import annotations

import pytest

import mcp_client


@pytest.fixture(autouse=True)
def clear_mcp_tool_cache() -> None:
    mcp_client.reset_mcp_session()
    yield
    mcp_client.reset_mcp_session()


def test_mcp_connection_handshake() -> None:
    """Initialize completes over Streamable HTTP (official ``mcp`` client)."""
    mcp_client.ping_server()


def test_tool_discovery_returns_tools() -> None:
    tools = mcp_client.get_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 1
    first = tools[0]
    assert first.get("type") == "function"
    assert "function" in first
    assert "name" in first["function"]
