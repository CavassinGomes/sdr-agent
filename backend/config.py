from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import timedelta


class Settings(BaseSettings):
    SESSION_TIMEOUT: int = Field(30, env="SESSION_TIMEOUT")
    MONGODB_URI: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    OPENAI_API_KEY: str | None = Field(None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4", env="OPENAI_MODEL")
    PIPEFY_API_URL: str | None = Field("https://api.pipefy.com/graphql", env="PIPEFY_API_URL")
    PIPEFY_TOKEN: str | None = Field(None, env="PIPEFY_TOKEN")
    CALENDAR_BASE_URL: str | None = Field(None, env="CALENDAR_BASE_URL")
    CALENDAR_API_KEY: str | None = Field(None, env="CALENDAR_API_KEY")
    
    CAL_EVENT_TYPE_ID: str = Field("test_event_type_id", env="CAL_EVENT_TYPE_ID")
    PIPEFY_PIPE_ID: str = Field("test_pipe_id", env="PIPEFY_PIPE_ID")

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()