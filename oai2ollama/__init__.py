from ._app import app


def start():
    import uvicorn

    uvicorn.run(app, host="localhost", port=11434)


__all__ = ["app", "start"]
