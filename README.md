---
title: Meridian Electronics — Customer Support
emoji: 🏬
colorFrom: gray
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# Meridian Electronics — Customer Support Chatbot

Production-style prototype: a Gradio chat UI backed by **OpenAI gpt-4o-mini** and a **remote MCP server** (Streamable HTTP). All product, order, and authentication operations go through MCP tools — the app does not talk to a database directly.

## Features

- **Authentication** — email + PIN via MCP (before orders or order history); Gradio session state tracks `is_authenticated` / `customer_email` after successful verification.
- **Products** — availability, search, and details via MCP tools.
- **Orders** — place orders and view history through MCP.
- **Resilient behavior** — OpenAI and MCP failures surface as short, user-friendly messages (no stack traces in the UI).

## Local setup

1. **Clone or copy** this `meridian-chatbot` folder.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** — copy the example file and add your key:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY` to your OpenAI API key. Do not commit `.env` (it is listed in `.gitignore`).

5. **Run the app**:

   ```bash
   python app.py
   ```

   Open the URL shown in the terminal (by default Gradio listens on `http://127.0.0.1:7860`). The server binds to `0.0.0.0` and port `7860` (or the `PORT` environment variable if set), which matches Hugging Face Spaces.

## Deploying to Hugging Face Spaces

1. Create a **new Space** with SDK **Gradio** and hardware as needed.

2. Upload this project (or connect a Git repository) so the Space root contains `app.py`, `chatbot.py`, `mcp_client.py`, `requirements.txt`, and `README.md`.

3. In the Space **Settings → Repository secrets**, add:

   - `OPENAI_API_KEY` — your OpenAI API key (required).

   Spaces inject secrets as environment variables; `python-dotenv` in `app.py` / `chatbot.py` also loads a `.env` file if you use one locally, but on Spaces you typically rely on secrets only.

4. **Push** your code. The Space runs `python app.py` automatically when `app.py` is the entry file.

Ensure `requirements.txt` matches the Space runtime (Python 3.10+ recommended).

## Tests

From this directory, with dependencies installed:

```bash
python -m pytest tests/ -v
```

`tests/test_mcp_client.py` hits the real MCP endpoint (needs network). `tests/test_chatbot.py` mocks OpenAI and does not call the live API.

## Project layout

| File | Role |
|------|------|
| `app.py` | Gradio `ChatInterface`, launch on `0.0.0.0`, auth `gr.State` |
| `chatbot.py` | System prompt, OpenAI loop, MCP tool execution |
| `mcp_client.py` | Official `mcp` SDK, Streamable HTTP transport |
| `tests/` | Pytest: MCP connectivity, tool discovery, chatbot reply shape |
| `.env.example` | Template for `OPENAI_API_KEY` |
| `requirements.txt` | Python dependencies |

The default MCP URL is in `mcp_client.py` (same hosted Meridian order server). Override with environment variable `MCP_SERVER_URL` if needed. Tools are discovered at runtime — tool names are not hardcoded for discovery.

## License

Use and modify for your Meridian Electronics prototype as needed.
