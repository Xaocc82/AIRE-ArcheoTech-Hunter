from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARCHEOTECH_")

    database_url: str = ""
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "archeotech"
    database_user: str = "archeotech"
    database_password: str = "archeotech"

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.database_url:
            self.database_url = URL.create(
                "postgresql+psycopg",
                username=self.database_user,
                password=self.database_password,
                host=self.database_host,
                port=self.database_port,
                database=self.database_name,
            ).render_as_string(hide_password=False)
        return self
