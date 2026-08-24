from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MetaboSync"
    API_V1_STR: str = "/api/v1"
    
    # --- Authentication Settings ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days in minutes
    SECRET_KEY: str = "a-very-secure-secret-key-for-metabosync-123" 

    class Config:
        case_sensitive = True

settings = Settings()