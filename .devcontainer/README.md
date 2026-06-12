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

## Browser Terminal

The image includes `ttyd` for a terminal-only browser page.

Start it inside the codespace:

```bash
start-browser-terminal
```

Codespaces forwards port `7681` as private. Open the forwarded port from the Codespaces **Ports** tab or use the port URL shown by GitHub.

Keep the port visibility private. This terminal is a shell in your codespace.
