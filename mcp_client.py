"""
MCP Streamable HTTP client for Meridian order MCP server.

Uses the official ``mcp`` Python SDK (``streamable_http_client`` + ``ClientSession``)
so initialize, session headers, and Streamable HTTP semantics match the spec.

Tools are discovered via ``list_tools()`` — never hardcoded.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import os
import threading
from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, TextContent, Tool

logger = logging.getLogger(__name__)

DEFAULT_MCP_URL = os.environ.get(
    "MCP_SERVER_URL",
    "https://order-mcp-74afyau24q-uc.a.run.app/mcp",
).rstrip("/")

# Gradio calls MCP from worker threads; always run asyncio on a fresh loop in a
# dedicated thread to avoid clashing with any outer event loop.
_mcp_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="mcp-async",
)


class MCPClientError(Exception):
    """Raised when the MCP server returns an error or invalid payload."""

    def __init__(self, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.recoverable = recoverable


def _run_mcp_coroutine(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async MCP coroutine from synchronous Gradio / test code."""
    fut = _mcp_executor.submit(asyncio.run, coro)
    return fut.result(timeout=180)


def _tool_to_descriptor_dict(tool: Tool) -> dict[str, Any]:
    schema = tool.inputSchema
    if schema is None:
        schema = {"type": "object", "properties": {}}
    elif not isinstance(schema, dict):
        schema = {"type": "object", "properties": {}}
    return {
        "name": tool.name,
        "description": tool.description or "",
        "inputSchema": schema,
    }


def _format_call_tool_result(result: CallToolResult) -> str:
    """Flatten MCP CallToolResult into a single string for the LLM."""
    if result.isError:
        parts: list[str] = []
        for block in result.content:
            if isinstance(block, TextContent):
                parts.append(block.text)
            else:
                parts.append(str(block))
        return "Error: " + ("\n".join(parts).strip() or "unknown tool error")

    chunks: list[str] = []
    for block in result.content:
        if isinstance(block, TextContent):
            chunks.append(block.text)
        else:
            chunks.append(str(block))
    if chunks:
        return "\n".join(chunks).strip()
    if result.structuredContent is not None:
        return json.dumps(result.structuredContent, ensure_ascii=False)[:12000]
    return ""


async def _session_list_tools_openai(url: str) -> list[dict[str, Any]]:
    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            return [mcp_tool_to_openai_function(_tool_to_descriptor_dict(t)) for t in listed.tools]


async def _session_call_tool(url: str, name: str, arguments: dict[str, Any]) -> str:
    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments=arguments)
            return _format_call_tool_result(result)


async def _session_ping(url: str) -> None:
    """Minimal handshake to verify connectivity."""
    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()


_client_lock = threading.RLock()
_cached_openai_tools: list[dict[str, Any]] | None = None
_cached_mcp_url: str | None = None


def _effective_url() -> str:
    return DEFAULT_MCP_URL


def mcp_tool_to_openai_function(tool: dict[str, Any]) -> dict[str, Any]:
    """Convert one MCP tool descriptor to OpenAI Chat Completions tool schema."""
    name = tool.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Tool missing string 'name'")
    desc = tool.get("description") or ""
    if not isinstance(desc, str):
        desc = str(desc)
    schema = tool.get("inputSchema") or {"type": "object", "properties": {}}
    if not isinstance(schema, dict):
        schema = {"type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc[:8000],
            "parameters": schema,
        },
    }


def get_tools() -> list[dict[str, Any]]:
    """
    Discover MCP tools and return them in OpenAI function-calling format.

    Results are cached per process for a given MCP URL.
    """
    global _cached_openai_tools, _cached_mcp_url
    url = _effective_url()
    with _client_lock:
        if _cached_openai_tools is not None and _cached_mcp_url == url:
            return list(_cached_openai_tools)
        try:
            tools = _run_mcp_coroutine(_session_list_tools_openai(url))
            _cached_openai_tools = tools
            _cached_mcp_url = url
            return list(tools)
        except MCPClientError:
            raise
        except Exception as e:
            logger.exception("Unexpected error listing MCP tools")
            raise MCPClientError(
                f"Failed to list MCP tools: {e!s}",
                recoverable=True,
            ) from e


def refresh_tools_cache() -> list[dict[str, Any]]:
    """Clear tool cache and re-fetch."""
    global _cached_openai_tools, _cached_mcp_url
    with _client_lock:
        _cached_openai_tools = None
        _cached_mcp_url = None
    return get_tools()


def call_tool(tool_name: str, arguments: dict[str, Any] | None) -> str:
    """
    Execute an MCP tool by name. Returns text for the LLM or a clear error string.

    Does not raise on tool/MCP failures — callers rely on string content for the model.
    """
    if not tool_name or not isinstance(tool_name, str):
        return "Error: invalid tool name."
    args = arguments if isinstance(arguments, dict) else {}
    url = _effective_url()
    try:
        return _run_mcp_coroutine(_session_call_tool(url, tool_name, args))
    except MCPClientError as e:
        logger.warning("MCP tool call failed (%s): %s", tool_name, e)
        return f"Error: {e!s}"
    except Exception as e:
        logger.exception("Unexpected MCP tool error (%s)", tool_name)
        return f"Error: unexpected failure calling {tool_name}: {e!s}"


def ping_server(url: str | None = None) -> None:
    """
    Verify MCP Streamable HTTP connectivity (initialize only).

    Raises MCPClientError or the underlying exception on failure — for tests.
    """
    u = (url or _effective_url()).rstrip("/")
    try:
        _run_mcp_coroutine(_session_ping(u))
    except Exception as e:
        raise MCPClientError(f"MCP ping failed: {e!s}", recoverable=True) from e


def reset_mcp_session() -> None:
    """Clear cached tool list (each tool call uses a fresh SDK session)."""
    global _cached_openai_tools, _cached_mcp_url
    with _client_lock:
        _cached_openai_tools = None
        _cached_mcp_url = None
