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

BASE_DIR = Path(__file__).resolve.parent
os_name = platform.system()

if os_name == "Darwin":
    load_dotenv(BASE_DIR / ".env.mac", override=True)
elif os_name == "Linux":
    load_dotenv(BASE_DIR / ".env.linux", override=True)

LLM_MODEL_HOST = os.getenv("MODEL_HOST")
LLM_MODEL = os.getenv("MODEL")
PORT = os.getenv("PORT")

quote = """Hi,

Thanks for your RFQ. We can offer the following:

P/N: TRAIN-PN-004
Qty: 3 EA
Condition: Inspected/Tested, with tags from our repair station
Price: USD 14,625.00 total, outright sale
Lead time: Stock, ships same day

Regards,
Northwind Aero Spares"""

MAX_ATTEMPTS = 3
MAX_VALIDATION_ATTEMPTS = 2
TIMEOUT = 30
RETRY_DELAY = 2

class Conditions(str, Enum):
    OVERHAUL = "OH"
    SERVICABLE = "SV"
    NEW = "NE"

class Sales(str, Enum):
    OUTRIGHT = "OUTRIGHT"
    EXCHANGE = "EXCHANGE"

class Quote(BaseModel):
    part_number: str
    quantity: int
    condition: Conditions | None
    currency: str
    unit_price: Decimal
    sale_basis: Sales

client = Client(host=LLM_MODEL_HOST, timeout=TIMEOUT)
validation_failures = 0

for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        response: ChatResponse = client.chat(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': quote}],
            think=True,
            stream=False,
            format=Quote.model_json_schema()
        )
        print("RAW:", response.message.content)
        quote_result = Quote.model_validate_json(response.message.content)
    except ConnectionError:
        print(f"Attempt {attempt}/{MAX_ATTEMPTS}: model server not reachable at localhost:{PORT}.")
    except httpx.TimeoutException:
         print(f"Attempt {attempt}/{MAX_ATTEMPTS}: no response within {TIMEOUT}s (server reachable, generation too slow).")
    except ValidationError as err:
        validation_failures += 1
        print(f"Attempt {attempt}/{MAX_ATTEMPTS}: output did not match Quote schema:\n{err}")
        if validation_failures >= MAX_VALIDATION_ATTEMPTS:
            print("Flag for review: model output failed validation twice. Not retrying.")
            sys.exit(1)
    else:
        print("VALIDATED:", quote_result)
        break

    if attempt < MAX_ATTEMPTS:
        time.sleep(RETRY_DELAY)
else:
    print(f"Gave up after {MAX_ATTEMPTS} attempts.")
    sys.exit(1)