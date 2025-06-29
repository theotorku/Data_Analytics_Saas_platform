import os
from pydantic_settings import BaseSettings
from pydantic import model_validator, Field # Import model_validator and Field
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "Data Analytics SaaS Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    # The setup.sh script creates a .env file with SECRET_KEY
    # Fallback to a new secrets.token_urlsafe(32) if not in .env for some reason
    SECRET_KEY: str = secrets.token_urlsafe(32) # Default here, will be overridden by .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Supabase Settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None # Anon public key
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None # Service role key for admin actions

    # CORS
    # This field will be populated from the .env variable "CORS_ORIGINS" as a string.
    # Its name matches the .env variable (case-sensitively due to Config.case_sensitive=True).
    CORS_ORIGINS_STR: str = Field(default="http://localhost:3000,http://localhost:5173", validation_alias=None, alias="CORS_ORIGINS")

    # This is the field we will actually use in the application, populated by the validator.
    # It's given a distinct name from the environment variable to avoid parsing conflicts.
    CORS_ORIGINS_LIST: List[str] = []

    @model_validator(mode='after')
    def _assemble_cors_origins_list(self) -> 'Settings':
        # self.CORS_ORIGINS_STR is populated by the .env variable "CORS_ORIGINS" via the alias
        if isinstance(self.CORS_ORIGINS_STR, str):
            self.CORS_ORIGINS_LIST = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(',') if origin.strip()]
        else:
            self.CORS_ORIGINS_LIST = []
        return self

    # External APIs (examples, add more as needed)
    OPENAI_API_KEY: Optional[str] = None # Default None, overridden by .env
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")

    # Email Configuration
    ENABLE_EMAIL: bool = True # Default, can be overridden by env var
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = True
    # REQUIRE_EMAIL_VERIFICATION: bool = True # Example if needed

    # Logging
    LOG_LEVEL: str = "INFO" # Default, overridden by .env

    # Redis (Removed, Supabase handles DB caching, consider if needed for other purposes later)
    # REDIS_URL: Optional[str] = None

    # File Upload Settings (example)
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["csv", "xlsx", "xls", "json", "txt"]


    model_config = {
        "case_sensitive": True,
        "env_file": ".env", # Relative to where python process is run (saas-platform/backend)
        "env_file_encoding": 'utf-8',
        "extra": 'ignore' # Allow and ignore extra fields from .env file
    }

settings = Settings()

# Ensure upload and log directories exist (also done in main.py but good here too)
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
# logs dir is usually relative to app root (saas-platform/backend/logs)
# if UPLOAD_FOLDER is also relative to app root:
# os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", settings.UPLOAD_FOLDER), exist_ok=True)
# For now, assume UPLOAD_FOLDER is relative to where app is run.
# The main.py creates "logs" and config.py creates "uploads".
# The docker-compose maps volumes to /app/uploads and /app/logs.
# The backend Dockerfile creates /app/uploads and /app/logs.
# Let's ensure this config doesn't conflict with those.
# It's better if these are absolute paths or clearly defined relative paths.
# For now, the simple os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True) is fine for local.
