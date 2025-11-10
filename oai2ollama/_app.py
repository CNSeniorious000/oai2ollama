import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from .config import env

# import logging



# Set logging
# logging.basicConfig(level=logging.ERROR)
# logger = logging.getLogger(__name__)

app = FastAPI()


def _new_client():
    from httpx import AsyncClient

    return AsyncClient(base_url=str(env.base_url), headers={"Authorization": f"Bearer {env.api_key}"}, timeout=60, http2=True, follow_redirects=True)


@app.get("/api/tags")
async def models():
    async with _new_client() as client:
        res = await client.get("/models")
        res.raise_for_status()
        try:
            data = res.json()["data"]
        except (KeyError, TypeError):
            data = []
        models_map = {i["id"]: {"name": i["id"], "model": i["id"]} for i in data} | {i: {"name": i, "model": i} for i in env.extra_models}
        return {"models": list(models_map.values())}


@app.post("/api/show")
async def show_model():
    return {
        "model_info": {"general.architecture": "CausalLM"},
        "capabilities": ["completion", *env.capabilities],
    }


@app.get("/v1/models")
async def list_models():
    async with _new_client() as client:
        res = await client.get("/models")
        res.raise_for_status()
        return res.json()


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()

    if data.get("stream", False):

        async def stream():
            async with _new_client() as client, client.stream("POST", "/chat/completions", json=data) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

        return StreamingResponse(stream(), media_type="text/event-stream")

    else:
        async with _new_client() as client:
            res = await client.post("/chat/completions", json=data)
            res.raise_for_status()
            return res.json()

@app.post("/api/chat")
async def ollama_chat(request: Request):
    data = await request.json()
    # logger.debug(f"Received request: {data}")

    # Check if steam
    stream = data.get("stream", False)

    # Base OpenAI payload
    openai_data = {
        "model": data.get("model", "default"),
        "messages": [],
        "stream": stream,
    }

    ROLE_MAP = {"user": "user", "assistant": "assistant", "system": "system"}
    openai_data["messages"] = [
        {
            "role": ROLE_MAP.get(msg.get("role"), "user"),
            "content": msg.get("content", ""),
        }
        for msg in data.get("messages", [])
    ]

    for opt in ("temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"):
        if opt in data:
            openai_data[opt] = data[opt]

    # logger.debug(f"Sending to OpenAI: {openai_data}")

    if stream:
        # Steam = True
        async def stream_ollama_response():
            async with _new_client() as client, client.stream("POST", "/chat/completions", json=openai_data) as response:
                response.raise_for_status()
                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and chunk["choices"]:
                                choice = chunk["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    content = choice["delta"]["content"]
                                    if content:
                                        full_content += content
                                        ollama_chunk = {
                                            "model": chunk.get("model", openai_data["model"]),
                                            "created_at": chunk.get("created", 0),
                                            "message": {
                                                "role": "assistant",
                                                "content": content,
                                            },
                                            "done": False,
                                        }
                                        yield json.dumps(ollama_chunk) + "\n"
                        except json.JSONDecodeError:
                            continue
                # Send final done message with usage stats if available
                final_message = {
                    "model": openai_data["model"],
                    "created_at": 0,
                    "message": {
                        "role": "assistant",
                        "content": "",
                    },
                    "done": True,
                    "total_duration": 0,
                    "load_duration": 0,
                    "prompt_eval_count": 0,
                    "prompt_eval_duration": 0,
                    "eval_count": len(full_content.split()),
                    "eval_duration": 0,
                }
                yield json.dumps(final_message) + "\n"

        # logger.debug("Returning streaming response")
        return StreamingResponse(stream_ollama_response(), media_type="application/x-ndjson")
    else:
        # Steam = False
        async with _new_client() as client:
            res = await client.post("/chat/completions", json=openai_data)
            res.raise_for_status()
            response_json = res.json()
            # logger.debug(f"Received from OpenAI: {response_json}")

            usage = response_json.get("usage", {})
            ollama_response = {
                "model": response_json.get("model", openai_data["model"]),
                "created_at": response_json.get("created", 0),
                "message": {
                    "role": "assistant",
                    "content": response_json["choices"][0]["message"]["content"],
                },
                "done": True,
                **(
                    {
                        "total_duration": usage.get("total_tokens", 0) * 1000,
                        "load_duration": 0,
                        "prompt_eval_count": usage.get("prompt_tokens", 0),
                        "prompt_eval_duration": 0,
                        "eval_count": usage.get("completion_tokens", 0),
                        "eval_duration": 0,
                    }
                    if usage
                    else {}
                ),
            }
            # logger.debug(f"Returning Ollama response: {ollama_response}")
            return ollama_response

@app.get("/api/version")
async def ollama_version():
    return {"version": "0.12.10"}
