"""Per-machine model settings, loaded from .env.mac (macOS) or .env.linux (Linux)."""
import os
import platform
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # project root (this file lives in quote_assistant/)
OS_NAME = platform.system()

if OS_NAME == "Darwin":
    load_dotenv(BASE_DIR / ".env.mac", override=True)
elif OS_NAME == "Linux":
    load_dotenv(BASE_DIR / ".env.linux", override=True)

LLM_MODEL_HOST = os.getenv("MODEL_HOST")
LLM_MODEL = os.getenv("MODEL")
