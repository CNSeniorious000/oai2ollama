FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

RUN uv sync

ENTRYPOINT ["uv", "run", "oai2ollama"]
CMD ["--help"]
