from ._app import app


def start():
    import uvicorn
    # 监听 IPv4 0.0.0.0，确保主机端口可访问
    uvicorn.run(app, host="0.0.0.0", port=11434)


__all__ = ["_app", "start"]
