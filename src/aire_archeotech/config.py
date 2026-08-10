from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARCHEOTECH_")

    database_url: str = (
        "postgresql+psycopg://archeotech:archeotech@localhost:5432/archeotech"
    )
