from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.2-11b-vision-instruct"
    
    llm_provider: str = "nvidia"
    llm_model: str = "meta/llama-3.2-11b-vision-instruct"
    llm_base_url: str = "https://integrate.api.nvidia.com/v1"
    llm_api_key: str = ""

    rag_enabled: bool = True
    rag_top_k: int = 5
    rag_relevance_threshold: float = 1.0
    chunk_size: int = 500
    chunk_overlap: int = 100

    database_url: str = "sqlite:///./chat.db"
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    cors_origins: str = "http://localhost:5173"
    jwt_secret_key: str = "c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def active_llm_api_key(self) -> str:
        return self.llm_api_key or self.nvidia_api_key

    @property
    def active_llm_base_url(self) -> str:
        return self.llm_base_url or self.nvidia_base_url

    @property
    def active_llm_model(self) -> str:
        return self.llm_model or self.nvidia_model


settings = Settings()

