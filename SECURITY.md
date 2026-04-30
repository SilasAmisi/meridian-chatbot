# Security policy

## Supported versions

This repository is a **prototype**. Security fixes are applied on a best-effort basis on the default branch (`main`).

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive findings.

1. Use [GitHub private vulnerability reporting](https://github.com/SilasAmisi/meridian-chatbot/security/advisories/new) if enabled for this repository, **or**
2. Contact the repository maintainers through a **private** channel (e.g. email or organization process), with enough detail to reproduce the issue without including customer data.

We aim to acknowledge reports within a few business days.

## Secrets and credentials

- **Never commit** `.env`, API keys, Hugging Face tokens, or customer data.
- Use **GitHub Actions secrets** for `HF_TOKEN`, `HF_SPACE_REPO`, and Space-side **`OPENAI_API_KEY`** — not plaintext in workflow YAML.
- Rotate any credential that may have been exposed (committed, pasted in an issue, or shared in logs).

## Threat model (short)

- The app calls **OpenAI** and a **remote MCP server** over HTTPS; traffic should use TLS only.
- Treat the Gradio UI as **user-facing**: do not surface stack traces, raw API errors, or internal paths to end users (the codebase follows this principle).

## Supply chain

- Dependencies are pinned with minimum versions in `requirements.txt`. Review Dependabot pull requests regularly.
- GitHub Actions use pinned major versions of official actions; consider pinning to commit SHAs for stricter supply-chain control.
