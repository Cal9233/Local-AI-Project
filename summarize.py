from ollama import chat, ChatResponse, Client
from pydantic import BaseModel, ValidationError
from decimal import Decimal
from enum import Enum
import sys
import httpx
import time
import os
from dotenv import load_dotenv
import platform
from pathlib import Path
import lmstudio as lms
import csv

BASE_DIR = Path(__file__).resolve().parent
EMAIL_DIR = BASE_DIR / "data" / "sample_email.txt"
os_name = platform.system()

if os_name == "Darwin":
    load_dotenv(BASE_DIR / ".env.mac", override=True)
elif os_name == "Linux":
    load_dotenv(BASE_DIR / ".env.linux", override=True)

LLM_MODEL_HOST = os.getenv("MODEL_HOST")
LLM_MODEL = os.getenv("MODEL")
PORT = os.getenv("PORT")
SUMMARY_PROMPT_V1 = """You are summarizing emails from supplier for Genthrust.
Do not make up your own information either if ambigous.

Only use values that appear in the email text.

- copy numbers exactly as written: no rounding, no converting, no adding up totals
- keep "each" vs "total" the way the email states it
- don't add anything that isn't in the email

Summarize this supplier email for a broker in exactly 3 sentences.
"""

def read_email(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

email = read_email(EMAIL_DIR)
model = lms.llm(LLM_MODEL)
chat = lms.Chat(SUMMARY_PROMPT_V1)
chat.add_user_message(email)
result = model.respond(chat, config={
    "temperature": 0.6
})
print(result)