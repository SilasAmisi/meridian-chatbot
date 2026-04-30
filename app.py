"""
Meridian Electronics customer support — Gradio entry point for Hugging Face Spaces.

Run: python app.py
"""

from __future__ import annotations

import logging
import os

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_AUTH_STATE: dict[str, object] = {
    "is_authenticated": False,
    "customer_email": None,
}


def main() -> None:
    # Import after dotenv so OPENAI_API_KEY is available for any import-time checks.
    from chatbot import chat_reply

    # Warm MCP tool cache when possible so the first user message is faster.
    try:
        import mcp_client

        mcp_client.get_tools()
        logger.info("MCP tools loaded successfully.")
    except Exception as e:
        logger.warning("Could not prefetch MCP tools (will retry on first chat): %s", e)

    auth_state = gr.State(DEFAULT_AUTH_STATE.copy())

    def ui_chat(message: str, history: list, auth: dict | None):
        reply, new_auth = chat_reply(message, history, auth)
        return reply, new_auth

    # With additional_inputs, Gradio requires each example as [message, *additional_values].
    _auth = DEFAULT_AUTH_STATE.copy()
    demo = gr.ChatInterface(
        fn=ui_chat,
        additional_inputs=[auth_state],
        additional_outputs=[auth_state],
        title="Meridian Electronics — Customer Support",
        description="Ask me about products, orders, or your account.",
        examples=[
            ["What products do you have available?", _auth.copy()],
            ["I want to check my order history", _auth.copy()],
            ["I need help placing an order", _auth.copy()],
        ],
        run_examples_on_click=False,
        cache_examples=False,
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
    )


if __name__ == "__main__":
    main()
