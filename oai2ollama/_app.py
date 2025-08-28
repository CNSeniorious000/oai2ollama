from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from .config import env

app = FastAPI()


def _new_client():
    from httpx import AsyncClient

    return AsyncClient(base_url=str(env.base_url), headers={"Authorization": f"Bearer {env.api_key}"}, timeout=60, http2=True, follow_redirects=True)


@app.get("/api/tags")
async def models():
    async with _new_client() as client:
        res = await client.get("/models")
        res.raise_for_status()
        models_map = {i["id"]: {"name": i["id"], "model": i["id"]} for i in res.json()["data"]} | {i: {"name": i, "model": i} for i in env.extra_models}
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

    # Base OpenAI payload
    openai_data = {
        "model": data.get("model", "default"),
        "messages": [],
        "stream": False,
    }

    # 1) Convert messages in one pass
    ROLE_MAP = {"user": "user", "assistant": "assistant", "system": "system"}
    openai_data["messages"] = [
        {
            "role": ROLE_MAP.get(msg.get("role"), "user"),
            "content": msg.get("content", ""),
        }
        for msg in data.get("messages", [])
    ]

    # 2) Bulk copy optional parameters
    for opt in ("temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"):
        if opt in data:
            openai_data[opt] = data[opt]

    async with _new_client() as client:
        res = await client.post("/chat/completions", json=openai_data)
        res.raise_for_status()
        response_json = res.json()

        # 3) Map back to Ollama format
        usage = response_json.get("usage", {})
        ollama_response = {
            "model": response_json.get("model", openai_data["model"]),
            "created_at": response_json.get("created", 0),
            "message": {
                "role": "assistant",
                "content": response_json["choices"][0]["message"]["content"],
            },
            "done": True,
            # optional usage fields
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
        return ollama_response

@app.get("/api/version")
async def ollama_version():
    return {"version": "0.11.4"}
