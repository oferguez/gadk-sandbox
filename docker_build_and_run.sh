#!/usr/bin/env bash

set -euo pipefail

read -r -p "Build gadk-sandbox-dev image? [y/N] " build_answer
case "$build_answer" in
    [yY]|[yY][eE][sS])
        docker build -t gadk-sandbox-dev -f .devcontainer/Dockerfile .devcontainer
        ;;
    *)
        echo "Skipping build."
        ;;
esac

read -r -p "Run gadk-sandbox-dev container? [y/N] " run_answer
case "$run_answer" in
    [yY]|[yY][eE][sS])
        docker run --rm -it \
            -p 7681:7681 \
            --env-file .env_local \
            -e CODEX_HOME=/root/.codex \
            -v codex-home:/root/.codex \
            -v "$PWD:/workspaces/gadk-sandbox" \
            -w /workspaces/gadk-sandbox \
            gadk-sandbox-dev \
            bash -lc 'codex-login-from-env && start-browser-terminal'
        ;;
    *)
        echo "Skipping run."
        ;;
esac
