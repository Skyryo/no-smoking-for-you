from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from .core.config import settings
from .core.auth import firebase_auth
from .routers import upload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="No Smoking for You API",
    description="API for the No Smoking for You application - Image Upload Service",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
from .routers import upload, websocket
app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["upload"])
app.include_router(websocket.router, prefix=settings.API_PREFIX, tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting No Smoking for You API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize Firebase Auth
    try:
        # Firebase is already initialized in auth.py
        logger.info("Firebase Authentication initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "No Smoking for You API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }
