from ollama import ChatResponse, Client
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

BASE_DIR = Path(__file__).resolve().parent
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

SYSTEM_PROMPT_V1 = """You extract data from supplier quotes for Genthrust.
Do not add fields of information that are not in the schema, do not make up your own information either if ambigous.

Return only the fields in the schema. 
Only use values that appear in the quote text.

Condition codes:
- OH = overhauled
- SV = serviceable
- NE = new
- "Inspected/Tested" (IP) counts as SV.
- If the quote does not clearly state a condition, use null.
"""

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

def ask_model(quote_text: str) -> str:
    """Send SYSTEM_PROMPT_V1 and the quote as separate messages; return the raw reply text.

    Only the request differs per machine: LM Studio on the Mac, Ollama on Linux.
    """
    if os_name == "Darwin":
        model = lms.llm(LLM_MODEL)
        chat = lms.Chat(SYSTEM_PROMPT_V1)
        chat.add_user_message(quote_text)
        result = model.respond(chat, response_format=Quote.model_json_schema())
        return result.content

    client = Client(host=LLM_MODEL_HOST, timeout=TIMEOUT)
    response: ChatResponse = client.chat(
        model=LLM_MODEL,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT_V1},
            {'role': 'user', 'content': quote_text},
        ],
        think=True,
        stream=False,
        format=Quote.model_json_schema()
    )
    return response.message.content


def main():
    validation_failures = 0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            raw = ask_model(quote)
            print("RAW:", raw)
            quote_result = Quote.model_validate_json(raw)
        except ConnectionError:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: model server not reachable at {LLM_MODEL_HOST}.")
        except httpx.TimeoutException:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: no response within {TIMEOUT}s (server reachable, generation too slow).")
        except lms.LMStudioError as err:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: LM Studio request failed ({type(err).__name__}): {err}")
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


if __name__ == "__main__":
    main()
