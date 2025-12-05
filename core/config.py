from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    APP_NAME: str = "ai-assistant"
    ENV: str = "dev"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    DATABASE_URL: str

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-70b-versatile"

    SERPAPI_KEY: str | None = None

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_DIR: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()
