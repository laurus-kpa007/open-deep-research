"""CORS configuration for production deployment."""

import os
from typing import List

def get_cors_origins() -> List[str]:
    """Get CORS origins from environment variables."""
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    # Split by comma and strip whitespace
    origins = [origin.strip() for origin in cors_origins.split(",")]

    # Add default origins if not in production
    if os.getenv("ENVIRONMENT", "development") == "development":
        default_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
        for origin in default_origins:
            if origin not in origins:
                origins.append(origin)

    return origins

def get_cors_config():
    """Get complete CORS configuration."""
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "expose_headers": ["*"]
    }