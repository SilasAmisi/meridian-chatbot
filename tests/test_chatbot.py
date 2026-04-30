"""Unit tests for chatbot reply wiring (OpenAI mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import chatbot


def _fake_completion(content: str | None = "Hello from Meridian support.", tool_calls=None):
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = tool_calls
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-fake"}, clear=False)
@patch("chatbot.mcp_client.get_tools", return_value=[])
@patch("chatbot.OpenAI")
def test_chatbot_returns_string_and_auth_dict(mock_openai, _mock_tools) -> None:
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value = _fake_completion()

    reply, auth = chatbot.chat_reply("Hi", [], None)

    assert isinstance(reply, str)
    assert len(reply) > 0
    assert isinstance(auth, dict)
    assert "is_authenticated" in auth
    assert "customer_email" in auth
    assert auth["is_authenticated"] is False
    assert auth["customer_email"] is None


@patch.dict("os.environ", {"OPENAI_API_KEY": ""})
def test_chatbot_missing_key_returns_tuple() -> None:
    reply, auth = chatbot.chat_reply("Hi", [], {"is_authenticated": True, "customer_email": "a@b.c"})
    assert "OPENAI_API_KEY" in reply
    assert auth["is_authenticated"] is True
    assert auth["customer_email"] == "a@b.c"
