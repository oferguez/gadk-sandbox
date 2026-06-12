FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm

ARG PYTHON_VERSION=3.11
ARG GOOGLE_ADK_VERSION=1.31.1
ARG CODEX_CLI_VERSION=0.87.0
ARG FIRECRAWL_CLI_VERSION=1.19.6

ENV GADK_VENV=/opt/gadk-venv
ENV PATH="${GADK_VENV}/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        "python${PYTHON_VERSION}" \
        "python${PYTHON_VERSION}-venv" \
        "python${PYTHON_VERSION}-dev" \
        python3-pip \
        graphviz \
        ttyd \
    && rm -rf /var/lib/apt/lists/*

RUN "python${PYTHON_VERSION}" -m venv "${GADK_VENV}" \
    && "${GADK_VENV}/bin/python" -m pip install --upgrade pip setuptools wheel \
    && "${GADK_VENV}/bin/python" -m pip install "google-adk==${GOOGLE_ADK_VERSION}" \
    && chown -R vscode:vscode "${GADK_VENV}"

RUN npm install -g \
        "@openai/codex@${CODEX_CLI_VERSION}" \
        "firecrawl-cli@${FIRECRAWL_CLI_VERSION}"

COPY bin/start-browser-terminal /usr/local/bin/start-browser-terminal
RUN chmod +x /usr/local/bin/start-browser-terminal

RUN python --version \
    && adk --version \
    && codex --version \
    && firecrawl --version
