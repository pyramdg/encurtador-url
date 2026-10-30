import os
from dataclasses import dataclass

@dataclass
class Settings:
    PROJECT_NAME: str = "Encurtador de URLs"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database (SQLite padrão para dev, PostgreSQL em produção)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./encurtador.db")
    
    # Configurações do encurtador
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    DEFAULT_EXPIRATION_DAYS: int = int(os.getenv("DEFAULT_EXPIRATION_DAYS", "7"))
    SHORT_CODE_MIN_LENGTH: int = 6
    SHORT_CODE_MAX_LENGTH: int = 8

settings = Settings()
