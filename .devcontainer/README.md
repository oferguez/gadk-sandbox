# Codespaces

This devcontainer builds a Codespaces image with these tools preinstalled:

- `google-adk` in `/opt/gadk-venv`
- Codex CLI from `@openai/codex`
- Firecrawl CLI from `firecrawl-cli`

The installs happen in `.devcontainer/Dockerfile`, so GitHub Codespaces prebuilds can cache the image. Enable prebuilds in the repository settings under Codespaces for the target branch to make later Codespace starts faster.

Set repository or user Codespaces secrets for any credentials you need:

- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `FIRECRAWL_API_KEY`

