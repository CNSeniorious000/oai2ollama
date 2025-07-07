from ._app import app


def start():
    import uvicorn

    uvicorn.run(app, host="::", port=11434)


__all__ = ["_app", "start"]
