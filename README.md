# Oai2Ollama

This is a CLI tool that starts a server that wraps an OpenAI-compatible API and expose an Ollama-compatible API,
which is useful for providing custom models for coding agents that don't support custom OpenAI APIs but do support Ollama
(like GitHub Copilot for VS Code).

## Usage

### with Python

You can run directly via `uvx` (if you have `uv` installed) or `pipx`:

```sh
uvx oai2ollama --help
```

```text
usage: oai2ollama [--api-key str] [--base-url HttpUrl]
options:
  --help              Show this help message and exit
  --api-key str       API key for authentication (required)
  --base-url HttpUrl  Base URL for the OpenAI-compatible API (required)
```

Or you can use a `.env` file to set the environment variables:

```properties
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
```

### with Docker

First, build the image:

```sh
docker build -t oai2ollama .
```

Then, run the container with your credentials:

```sh
docker run -p 11434:11434 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_BASE_URL="your_base_url" \
  oai2ollama
```

Or you can pass these as command line arguments:

```sh
docker run -p 11434:11434 oai2ollama --api-key your_api_key --base-url your_base_url
```
