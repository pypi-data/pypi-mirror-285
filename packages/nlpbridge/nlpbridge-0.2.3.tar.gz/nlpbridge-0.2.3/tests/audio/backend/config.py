from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "audio-backend"
    API_V1_STR: str = "/api/v1"


settings = Settings()
