---
title: Introduction
icon: lucide/anchor
---

# :fontawesome-brands-openai:{ title="OpenAI-compatible API" } :lucide-chevrons-right:{ style="opacity: 0.3" title="👉" } :simple-ollama:{ title="Ollama-compatible API" }

[`oai2ollama`](https://pypi.org/project/oai2ollama/) is a lightweight FastAPI server that translates an OpenAI ChatCompletions API endpoint into an Ollama-compatible endpoint. It allows you to use custom LLM providers for coding agents that don't support custom OpenAI APIs but do support Ollama (like GitHub Copilot for VS Code).

## Quick Start

### with Python

You can run directly via `uvx` (if you have `uv` installed) or `pipx`:

```sh
uvx oai2ollama --help
```

```text
usage: oai2ollama [--api-key str] [--base-url HttpUrl] [--capabilities list[str]] [--models list[str]] [--host str]
options:
  --help, -h                    Show this help message and exit
  --api-key str                 API key for authentication (required)
  --base-url HttpUrl            Base URL for the OpenAI-compatible API (required)
  --capabilities, -c list[str]  Extra capabilities to mark the model as supporting
  --models, -m list[str]        Extra models to include in the /api/tags response
  --host str                    IP / hostname for the API server (default: localhost)
```

Or you can use a `.env` file:

```properties
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
HOST=0.0.0.0
CAPABILITIES=["vision","thinking"]
MODELS=["custom-model1","custom-model2"]
```

!!! tip ""

    To mark the model as supporting certain capabilities, use the `--capabilities` (or `-c`) option:

    `oai2ollama -c tools` or `oai2ollama --capabilities tools`

    `oai2ollama -c tools -c vision` or `oai2ollama --capabilities -c tools,vision`

    To support models that are not returned by the `/models` endpoint:

    `oai2ollama -m model1 -m model2` or `oai2ollama -m model1,model2`

    Capabilities currently used by Ollama are: `tools`, `insert`, `vision`, `embedding`, `thinking` and `completion`. We always include `completion`.

### with Docker

```sh
docker build -t oai2ollama .
docker run -p 11434:11434 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_BASE_URL="your_base_url" \
  oai2ollama
```

To listen on all interfaces:

```sh
docker run -p 11434:11434 oai2ollama --host "::"
```

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Ollama-compatible `/api/tags` and `/api/show` endpoints
- Streaming response support
- Configurable model list with extra models
- Customizable capabilities (tools, insert, vision, embedding, thinking)
