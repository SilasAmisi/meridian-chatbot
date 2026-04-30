---
title: Meridian Electronics — Customer Support
emoji: 🏬
colorFrom: gray
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# Meridian Electronics — Customer Support Chatbot

Production-style prototype: a Gradio chat UI backed by **OpenAI gpt-4o-mini** and a **remote MCP server** (Streamable HTTP). All product, order, and authentication operations go through MCP tools — the app does not talk to a database directly.

## Features

- **Authentication** — email + PIN via MCP (before orders or order history); Gradio session state tracks `is_authenticated` / `customer_email` after successful verification.
- **Products** — availability, search, and details via MCP tools.
- **Orders** — place orders and view history through MCP.
- **Resilient behavior** — OpenAI and MCP failures surface as short, user-friendly messages (no stack traces in the UI).

---

## Step-by-step: Run the project locally

### 1. Clone the repository

**Git (HTTPS):**

```bash
git clone https://github.com/SilasAmisi/meridian-chatbot.git
cd meridian-chatbot
```

If you use SSH, replace the URL with your SSH remote. On Windows, the same commands work in **PowerShell**, **Command Prompt**, or **Git Bash**.

### 2. Install requirements

Create and activate a virtual environment (recommended), then install dependencies:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use **Python 3.10+**.

### 3. Add `.env` locally

Copy the example env file and fill in your OpenAI key:

**Windows:**

```powershell
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Edit `.env` in your editor and set:

```env
OPENAI_API_KEY=sk-...your-real-key...
```

Do **not** commit `.env` — it is listed in `.gitignore`.

### 4. Run locally with `python app.py`

From the `meridian-chatbot` directory (with the virtual environment activated):

```bash
python app.py
```

Open the URL Gradio prints (typically **http://127.0.0.1:7860**). The app listens on `0.0.0.0` and port **7860** (or the `PORT` environment variable), which matches Hugging Face Spaces.

---

## Step-by-step: Hugging Face Space

### 5. Create a Hugging Face Space

1. Sign in at [huggingface.co](https://huggingface.co).
2. Click your avatar → **New Space** (or go to [huggingface.co/new-space](https://huggingface.co/new-space)).
3. Choose a **Space name** (for example `meridian-chatbot`) and owner (**User** or **Organization**).
4. Set **SDK** to **Gradio** (this project uses `app.py` as the entry file).
5. Choose visibility (**Public** or **Private**) and hardware if needed, then **Create Space**.

You will get a Space URL like:

`https://huggingface.co/spaces/<your-username>/<your-space-name>`

Remember **`<your-username>/<your-space-name>`** — you need it for git remotes and for GitHub Actions (as `HF_SPACE_REPO`).

### 6. Add `OPENAI_API_KEY` as a Space secret

1. Open your Space on Hugging Face.
2. Go to **Settings** (tab on the Space page).
3. Open **Repository secrets** (or **Variables and secrets** → secrets for the Space).
4. Add a new secret:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** your OpenAI API key (`sk-...`).

Save. The Space injects this as an environment variable at runtime, which `chatbot.py` reads via `os.environ` (and `python-dotenv` is optional on Spaces).

### 7. Push to Hugging Face to trigger deployment

The Space runs from the **Git repository** hosted on Hugging Face. Any push to that repo’s default branch (**`main`**) starts a new build and deployment.

**Option A — Push from your computer (first-time or manual deploy)**

1. Install the Hugging Face CLI (once): `pip install huggingface_hub`
2. Log in: `hf auth login` (paste a **write** token from [Settings → Access Tokens](https://huggingface.co/settings/tokens)), or non-interactive: `hf auth login --token YOUR_TOKEN --add-to-git-credential`.
3. In your local `meridian-chatbot` clone, add the Space as a remote (replace `YOUR_USER` and `YOUR_SPACE`):

   ```bash
   git remote add huggingface https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE.git
   ```

4. Push your `main` branch:

   ```bash
   git push huggingface main
   ```

If the Space already had an initial commit from the web UI, you may need **`git push --force huggingface main`** once to replace it with this repo — only do that if you are sure you will not lose wanted changes on the Space.

**Option B — Push to GitHub `main` to auto-deploy (recommended)**

This repository includes [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml). On every push to **`main`**, GitHub Actions **force-pushes** to your Space over HTTPS using **`HF_TOKEN`** (username is taken from `HF_SPACE_REPO`; no `pip`, `huggingface_hub`, `huggingface-cli`, or `hf` in the workflow). It uses **`actions/checkout@v4`** and sets **`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`** for Actions’ Node runtime.

**If the “Push” step logs `huggingface-cli` / pip warnings and exits with code 1:** your workflow on GitHub may still include a **`Set up Python` / `actions/setup-python`** step (this repo’s deploy workflow does **not**). Remove that step from `.github/workflows/deploy.yml` on **`main`** so the job is only **Checkout** + **Push** — `setup-python` is not needed for `git push` and the runner image can invoke HF’s deprecated CLI via Git credential helpers. The script also sets **`GIT_CONFIG_NOSYSTEM=1`** and **`GCM_INTERACTIVE=never`** to reduce helper interference.

1. In your **GitHub** repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Add **`HF_TOKEN`**: a Hugging Face [access token](https://huggingface.co/settings/tokens) with **write** permission (role **write** is enough to push to Spaces you own).
3. Add **`HF_SPACE_REPO`**: the Space id in the form **`username/space-name`** (example: `swawire/meridian-chatbot`). No `https://`, no `spaces/` prefix — only `owner/repo-style-name` as shown in the Space URL path after `/spaces/`.
4. Push (or merge) to **`main`** on GitHub. Open the **Actions** tab to confirm the **Deploy to Hugging Face Space** workflow succeeded.

If either secret is missing, the workflow fails with an error pointing you back to this README.

### Troubleshooting: deploy workflow fails

The workflow **validates secrets**, runs **`git ls-remote`** (auth check), then **`git push`**. In the Actions log, expand the groups **“Checking secrets”**, **“Pre-flight”**, and **“Configure git and push”** to see which step failed.

| Symptom | What to check |
|--------|----------------|
| **HF_TOKEN is empty or not set** | Add a **repository** secret named `HF_TOKEN` under **Settings → Secrets and variables → Actions** (not only Environment secrets, unless the job targets that environment). |
| **HF_SPACE_REPO wrong format** | Must be `owner/space` only — no `https://`, no leading `spaces/`. Copy from the Space URL: `https://huggingface.co/spaces/OWNER/SPACE` → use `OWNER/SPACE`. |
| **`git ls-remote` failed** | Token lacks **write** access, wrong Space name, Space deleted, or token owner ≠ Space owner. Create a new [HF token](https://huggingface.co/settings/tokens) with **Write** and try again. |
| **`git push` failed after ls-remote OK** | Rare (permissions changed mid-run, or branch protection on the Space side). Re-run the job; confirm the Space still exists. |
| **`huggingface-cli` / pip in the log** | Remove any **`actions/setup-python`** step from this workflow. The template job is **only** checkout + shell steps. |

After changing secrets, use **Re-run failed jobs** — no new commit is required.

---

## Tests

From the `meridian-chatbot` directory, with dependencies installed:

```bash
python -m pytest tests/ -v
```

`tests/test_mcp_client.py` hits the real MCP endpoint (needs network). `tests/test_chatbot.py` mocks OpenAI and does not call the live API.

## Project layout

| Path | Role |
|------|------|
| `app.py` | Gradio `ChatInterface`, launch on `0.0.0.0`, auth `gr.State` |
| `chatbot.py` | System prompt, OpenAI loop, MCP tool execution |
| `mcp_client.py` | Official `mcp` SDK, Streamable HTTP transport |
| `.github/workflows/deploy.yml` | Deploy to Hugging Face Space (`permissions: contents: read`) |
| `.github/dependabot.yml` | Weekly pip + monthly GitHub Actions dependency updates |
| `tests/` | Pytest: MCP connectivity, tool discovery, chatbot reply shape |
| `.env.example` | Template for `OPENAI_API_KEY` (never commit real `.env`) |
| `requirements.txt` | Python dependencies |
| `SECURITY.md` | Vulnerability reporting and secret-handling expectations |
| `CONTRIBUTING.md` | How to contribute and run tests |
| `LICENSE` | MIT |

The default MCP URL is in `mcp_client.py`. Override with **`MCP_SERVER_URL`** in `.env` if needed. Tools are discovered at runtime — tool names are not hardcoded for discovery.

## Security

- **Secrets:** Keep `OPENAI_API_KEY` and any Hugging Face tokens in **`.env` locally** (gitignored) and in **GitHub / Hugging Face secret stores** for CI and Spaces — never in source or issues.
- **Workflow:** The deploy workflow uses **least-privilege** `permissions: contents: read`; Hugging Face push auth uses **`HF_TOKEN`** / **`HF_SPACE_REPO`** repository secrets only.
- **Reporting:** See **[SECURITY.md](SECURITY.md)** for how to report vulnerabilities responsibly.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Meridian Electronics (prototype).
