FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install .

ENTRYPOINT ["oai2ollama"]
CMD ["--help"]