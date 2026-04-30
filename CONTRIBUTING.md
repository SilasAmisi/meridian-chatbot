# Contributing

## Basics

1. Fork or branch from **`main`**.
2. Install dependencies (`pip install -r requirements.txt`) and run **`python -m pytest tests/ -v`** before opening a pull request.
3. Do **not** commit `.env`, API keys, or tokens. Use `.env.example` only as a template.

## Pull requests

- Describe the change and any security-relevant behavior (new network calls, new secrets, etc.).
- Keep diffs focused on the stated goal.

## Security

See **[SECURITY.md](SECURITY.md)** for reporting vulnerabilities.
