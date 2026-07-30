import re
from os import getenv
from sys import stderr
from typing import Literal, Self

from pydantic import Field, HttpUrl, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, CliSuppress


class InvalidContextLengthError(ValueError):
    def __init__(self):
        super().__init__("invalid context length")


class Settings(BaseSettings):
    model_config = {
        "cli_parse_args": True,
        "cli_kebab_case": True,
        "cli_ignore_unknown_args": True,
        "extra": "ignore",
        "cli_shortcuts": {
            "capabilities": "c",
            "models": "m",
            "context-lengths": "l",
        },
    }

    api_key: str = Field(getenv("OPENAI_API_KEY", ...), description="API key for authentication")  # type: ignore
    base_url: HttpUrl = Field(getenv("OPENAI_BASE_URL", ...), description="Base URL for the OpenAI-compatible API")  # type: ignore
    capacities: CliSuppress[list[Literal["tools", "insert", "vision", "embedding", "thinking"]]] = Field([], repr=False)
    capabilities: list[Literal["tools", "insert", "vision", "embedding", "thinking"]] = []
    host: str = Field("localhost", description="IP / hostname for the API server")
    extra_models: list[str] = Field([], description="Extra models to include in the /api/tags response", alias="models")
    context_lengths: dict[str, int] = Field({}, description='Context length for specific models, e.g. {"model-name": 4096}')

    @field_validator("context_lengths", mode="before")
    @classmethod
    def _parse_context_lengths(cls, value):
        def _parse_context_length(value: int | str) -> int:
            if isinstance(value, int):
                return value

            parsed = re.fullmatch(r"\s*(\d+)\s*([kKmM]?)\s*", value)
            if not parsed:
                raise InvalidContextLengthError

            amount = int(parsed.group(1))
            suffix = parsed.group(2).lower()
            if suffix == "k":
                return amount * 1000
            if suffix == "m":
                return amount * 1000 * 1000
            return amount

        if not isinstance(value, dict):
            return value
        return {k: _parse_context_length(v) for k, v in value.items()}

    @model_validator(mode="after")
    def _warn_legacy_capacities(self: Self):
        if self.capacities:
            print("\n  Warning: 'capacities' is a previous typo, please use 'capabilities' instead.\n", file=stderr)
            self.capabilities.extend(self.capacities)
        return self


try:
    env = Settings()  # type: ignore
    print(env, file=stderr)
except ValidationError as err:
    print("\n  Error: invalid config:\n", file=stderr)
    for error in err.errors():
        print(" ", "".join(f".{x}" if isinstance(x, str) else f"[{x}]" for x in error["loc"]).lstrip(".") + ":", error["msg"], file=stderr)
    print(file=stderr)
    exit(1)
