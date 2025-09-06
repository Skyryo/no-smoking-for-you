import os
from typing import Optional

class Settings:
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "no-smoking-hackathon")
    
    # Google Cloud Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "no-smoking-hackathon")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "no-smoking-hackathon-bucket")
    
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE: int = 1024  # 1KB
    ALLOWED_CONTENT_TYPES: list = ["image/jpeg", "image/png"]
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png"]
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "https://localhost:3000",
        # Add Firebase Hosting domain when available
        "https://no-smoking-hackathon.web.app",
        "https://no-smoking-hackathon.firebaseapp.com"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

settings = Settings()
