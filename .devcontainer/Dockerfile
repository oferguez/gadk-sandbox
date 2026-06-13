FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm

ARG PYTHON_VERSION=3.11
ARG GOOGLE_ADK_VERSION=1.31.1
ARG CODEX_CLI_VERSION=latest
ARG FIRECRAWL_CLI_VERSION=1.19.6
ARG TTYD_VERSION=1.7.7

ENV GADK_VENV=/opt/gadk-venv
ENV PATH="${GADK_VENV}/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        "python${PYTHON_VERSION}" \
        "python${PYTHON_VERSION}-venv" \
        "python${PYTHON_VERSION}-dev" \
        python3-pip \
        ca-certificates \
        graphviz \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN case "$(uname -m)" in \
        x86_64) ttyd_arch="x86_64" ;; \
        aarch64) ttyd_arch="aarch64" ;; \
        *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;; \
    esac \
    && wget -O /usr/local/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.${ttyd_arch}" \
    && chmod +x /usr/local/bin/ttyd

RUN "python${PYTHON_VERSION}" -m venv "${GADK_VENV}" \
    && "${GADK_VENV}/bin/python" -m pip install --upgrade pip setuptools wheel \
    && "${GADK_VENV}/bin/python" -m pip install "google-adk==${GOOGLE_ADK_VERSION}" \
    && chmod -R a+rX "${GADK_VENV}"

RUN npm install -g \
        "@openai/codex@${CODEX_CLI_VERSION}" \
        "firecrawl-cli@${FIRECRAWL_CLI_VERSION}"

COPY bin/start-browser-terminal /usr/local/bin/start-browser-terminal
COPY bin/codex-login-from-env /usr/local/bin/codex-login-from-env
RUN chmod +x /usr/local/bin/start-browser-terminal /usr/local/bin/codex-login-from-env

RUN python --version \
    && adk --version \
    && codex --version \
    && firecrawl --version \
    && ttyd --version
