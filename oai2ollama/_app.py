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

    # Convert Ollama format to OpenAI format
    openai_data = {
        "model": data.get("model", "default"),
        "messages": [],
        "stream": False  # Always set to False for non-streaming
    }

    # Convert Ollama messages to OpenAI format
    if "messages" in data:
        for msg in data["messages"]:
            role = msg.get("role", "user")
            if role == "user":
                openai_data["messages"].append({
                    "role": "user",
                    "content": msg.get("content", "")
                })
            elif role == "assistant":
                openai_data["messages"].append({
                    "role": "assistant",
                    "content": msg.get("content", "")
                })
            elif role == "system":
                openai_data["messages"].append({
                    "role": "system",
                    "content": msg.get("content", "")
                })

    # Add optional parameters
    if "temperature" in data:
        openai_data["temperature"] = data["temperature"]
    if "max_tokens" in data:
        openai_data["max_tokens"] = data["max_tokens"]
    if "top_p" in data:
        openai_data["top_p"] = data["top_p"]
    if "frequency_penalty" in data:
        openai_data["frequency_penalty"] = data["frequency_penalty"]
    if "presence_penalty" in data:
        openai_data["presence_penalty"] = data["presence_penalty"]

    # print(openai_data)
    # Always use non-streaming approach
    async with _new_client() as client:
        try:
            res = await client.post("/chat/completions", json=openai_data)
            # print(f"Response status: {res.status_code}")
            # print(f"Response headers: {res.headers}")

            # Try to get response text for debugging
            # response_text = res.text
            # print(f"Response text: {response_text}")

            res.raise_for_status()

            # Parse and return JSON
            response_json = res.json()

            # Convert OpenAI response to Ollama format
            ollama_response = {
                "model": response_json.get("model", openai_data.get("model", "default")),
                "created_at": response_json.get("created", 0),
                "message": {
                    "role": "assistant",
                    "content": response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                },
                "done": True
            }

            # Add optional fields if they exist
            if "usage" in response_json:
                ollama_response["total_duration"] = response_json["usage"].get("total_tokens", 0) * 1000  # rough estimate
                ollama_response["load_duration"] = 0  # not available in OpenAI response
                ollama_response["prompt_eval_count"] = response_json["usage"].get("prompt_tokens", 0)
                ollama_response["prompt_eval_duration"] = 0  # not available in OpenAI response
                ollama_response["eval_count"] = response_json["usage"].get("completion_tokens", 0)
                ollama_response["eval_duration"] = 0  # not available in OpenAI response

            return ollama_response

        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"Error type: {type(e)}")
            # Re-raise the exception to maintain the original behavior
            raise

@app.get("/api/version")
async def ollama_version():
    return {"version": "0.11.4"}
