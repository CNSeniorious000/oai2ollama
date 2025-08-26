from os import getenv
from sys import stderr
from typing import Literal, Self

from pydantic import Field, HttpUrl, ValidationError, model_validator
from pydantic_settings import BaseSettings, CliSuppress


class Settings(BaseSettings):
    model_config = {
        "cli_parse_args": True,
        "cli_kebab_case": True,
        "cli_ignore_unknown_args": True,
        "extra": "ignore",
        "cli_shortcuts": {
            "capabilities": "c",
            "models": "m",
        },
    }

    api_key: str = Field(getenv("OPENAI_API_KEY", ...), description="API key for authentication")  # type: ignore
    base_url: HttpUrl = Field(getenv("OPENAI_BASE_URL", ...), description="Base URL for the OpenAI-compatible API")  # type: ignore
    capacities: CliSuppress[list[Literal["tools", "insert", "vision", "embedding", "thinking"]]] = Field([], repr=False)
    capabilities: list[Literal["tools", "insert", "vision", "embedding", "thinking"]] = []
    host: str = Field("localhost", description="IP / hostname for the API server")
    models: list[str] = Field([], description="Extra models to include in the /api/tags response")

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
