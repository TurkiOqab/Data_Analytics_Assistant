"""Configuration module for Data Analytics Assistant."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Default model to use (free tier compatible)
DEFAULT_MODEL = "gemini-2.5-flash"

# Supported file extensions for dataset loading
SUPPORTED_EXTENSIONS = {
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".json": "json",
}


def validate_config():
    """Validate that required configuration is present."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add your API key to the .env file.\n"
            "Get your API key at: https://aistudio.google.com/apikey"
        )
    return True
