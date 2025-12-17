"""Configuration module for Data Analytics Assistant."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default model to use for chat completions
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Supported file extensions for dataset loading
SUPPORTED_EXTENSIONS = {
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".json": "json",
}


def validate_config():
    """Validate that required configuration is present."""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is not set. Please add your API key to the .env file.\n"
            "Get your API key at: https://console.groq.com"
        )
    return True
