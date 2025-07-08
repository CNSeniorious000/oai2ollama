# Oai2Ollama

This is a CLI tool that starts a server that wraps an OpenAI-compatible API and expose an Ollama-compatible API,
which is useful for providing custom models for coding agents that don't support custom OpenAI APIs but do support Ollama
(like GitHub Copilot for VS Code).

## Usage

### User can use `uvx` or `pipx` to directly use it:

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

### Docker Deployment
1. Build image:
```sh
docker build -t oai2ollama .
```

2. Run container:
```sh
docker run -it \
  -p 11434:11434 \
  -e OPENAI_API_KEY=your_api_key \
  -e OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1/ \
  oai2ollama
```

3. Windows users can use the startup script `start.bat`. It automatically create new container to update the environments.