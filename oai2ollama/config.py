from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "cli_parse_args": True,
        "cli_kebab_case": True,
        "cli_ignore_unknown_args": True,
        "env_prefix": "OPENAI_",
        "env_file": ".env",
    }

    api_key: str
    base_url: str


env = Settings()  # type: ignore

print(env)
