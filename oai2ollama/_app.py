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
        res = await client.get("/models")  # Replace with the actual API endpoint
        res.raise_for_status()

        # Get original models from API response
        original_models = [{"name": i["id"], "model": i["id"]} for i in res.json()["data"]]

        # Add additional models from config
        if env.models:
            additional_models = [{"name": model.strip(), "model": model.strip()}
                               for model in env.models.split(",") if model.strip()]
            original_models.extend(additional_models)

        print({"models": original_models})
        return {"models": original_models}


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


@app.get("/api/version")
async def ollama_version():
    return {"version": "0.11.4"}
