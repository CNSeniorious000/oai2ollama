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
usage: oai2ollama [--api-key str] [--base-url HttpUrl] [--capabilities list[str]] [--models list[str]] [--host str]
options:
  --help, -h                    Show this help message and exit
  --api-key str                 API key for authentication (required)
  --base-url HttpUrl            Base URL for the OpenAI-compatible API (required)
  --capabilities, -c list[str]  Extra capabilities to mark the model as supporting
  --models, -m list[str]        Extra models to include in the /api/tags response
  --host str                    IP / hostname for the API server (default: localhost)
```

> [!TIP]
> To mark the model as supporting certain capabilities, you can use the `--capabilities` (or `-c`) option with a list of strings. For example, the following two syntaxes are supported:
>
> `oai2ollama -c tools` or `oai2ollama --capabilities tools`
>
> `oai2ollama -c tools -c vision` or `oai2ollama --capabilities -c tools,vision`
>
> To support models that are not returned by the `/models` endpoint, use the `--models` (or `-m`) option to add them to the `/api/tags` response:
>
> `oai2ollama -m model1 -m model2` or `oai2ollama -m model1,model2`
>
> Capabilities currently [used by Ollama](https://github.com/ollama/ollama/blob/main/types/model/capability.go#L6-L11) are:
> `tools`, `insert`, `vision`, `embedding`, `thinking` and `completion`. We always include `completion`.

Or you can use a `.env` file to set these options:

```properties
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
HOST=0.0.0.0
CAPABILITIES=["vision","thinking"]
MODELS=["custom-model1","custom-model2"]
```

> [!WARNING]
> The option name `capacities` is deprecated. Use `capabilities` instead. The old name still works for now but will emit a deprecation warning.

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

To have the server listen on a different host, like all IPv6 interfaces, use the `--host` argument:

```sh
docker run -p 11434:11434 oai2ollama --host "::"
```
