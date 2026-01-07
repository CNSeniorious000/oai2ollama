---
icon: lucide/cog
---

# Configuration

## Environment Variables

| Variable          | CLI Flag               | Description                                        | Default     |
| ----------------- | ---------------------- | -------------------------------------------------- | ----------- |
| `OPENAI_API_KEY`  | `--api-key`            | API key for authentication                         | _required_  |
| `OPENAI_BASE_URL` | `--base-url`           | Base URL for OpenAI-compatible API                 | _required_  |
| `HOST`            | `--host`               | IP/hostname for the API server                     | `localhost` |
| `CAPABILITIES`    | `--capabilities`, `-c` | Extra capabilities to mark the model as supporting | `[]`        |
| `MODELS`          | `--models`, `-m`       | Extra models to include in `/api/tags`             | `[]`        |

## Capabilities

Capabilities indicate what features a model supports. Available capabilities:

- `tools` - Function calling / tools support
- `insert` - Insert mode
- `vision` - Vision / image input support
- `embedding` - Embedding generation
- `thinking` - Thinking mode
- `completion` - Always included, basic completion

### Setting Capabilities

```sh
# Single capability
oai2ollama -c tools

# Multiple capabilities (separate flags)
oai2ollama -c tools -c vision

# Multiple capabilities (comma-separated)
oai2ollama --capabilities tools,vision
```

## Extra Models

Add models that aren't returned by the upstream API:

```sh
# Multiple models (separate flags)
oai2ollama -m model1 -m model2

# Multiple models (comma-separated)
oai2ollama --models model1,model2
```

## Example .env File

```properties
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
HOST=0.0.0.0
CAPABILITIES=["vision","thinking"]
MODELS=["custom-model1","custom-model2"]
```

## Docker Example

```sh
docker run -p 11434:11434 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_BASE_URL="your_base_url" \
  -e CAPABILITIES='["vision","thinking"]' \
  oai2ollama
```

Or with CLI arguments:

```sh
docker run -p 11434:11434 \
  oai2ollama --api-key your_api_key --base-url your_base_url \
  --capabilities tools,vision --models custom-model
```
