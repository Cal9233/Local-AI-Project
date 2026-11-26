from ollama import ChatResponse, Client, ResponseError
from pydantic import BaseModel, Field, ValidationError
from decimal import Decimal
from enum import Enum
import sys
import httpx
import logging
import time
import lmstudio as lms

from config import OS_NAME, LLM_MODEL_HOST, LLM_MODEL

logger = logging.getLogger(__name__)

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

# V2 (lesson 4.2): several records per email, null price allowed, and an exact
# supporting phrase that code checks against the email.
SYSTEM_PROMPT_V2 = """You extract offers from aircraft-parts supplier emails.
Return {"quote_list": [...]} with one record per offer the buyer could accept on its own.
If the email makes no offer (e.g. no stock), return an empty quote_list.

Rules:
- Only use values that appear in the email. Never guess. If a field is not stated, use null.
- part_number: exactly as written.
- quantity: units in stock now; do not count units in repair or available later.
- condition: OH = overhauled, SV = serviceable (incl. "Inspected/Tested"), NE = new.
  As-removed, untested, or not stated -> null.
- currency: the ISO code (USD or EUR) only if the email states it; otherwise null.
- price: the number as a plain decimal (e.g. 3.450,00 -> 3450.00); null if no price is stated.
- price_basis: PER_UNIT if the price is per unit/each, LOT if it is a total for all units.
- sale_basis: OUTRIGHT or EXCHANGE. For exchanges, price is the exchange fee.
- core_charge: the amount owed if an exchange core is not returned; null for outright offers.
- price_phrase: copy the exact words from the email that state the price, character for character.
  null if no price is stated.
"""
PROMPT_VERSION = "V2"
MAX_ATTEMPTS = 3
MAX_VALIDATION_ATTEMPTS = 2
TIMEOUT = 60
RETRY_DELAY = 2

class Conditions(str, Enum):
    OVERHAUL = "OH"
    SERVICABLE = "SV"
    NEW = "NE"

class Sales(str, Enum):
    OUTRIGHT = "OUTRIGHT"
    EXCHANGE = "EXCHANGE"

class PriceBasis(str, Enum):
    PER_UNIT = "PER_UNIT"
    WHOLE_LOT = "LOT"

class Quote(BaseModel):
    part_number: str
    quantity: int = Field(gt=0)
    condition: Conditions | None
    currency: str | None
    # None = the email states no price; such quotes go to human review, never ranking.
    price: Decimal | None = Field(gt=0)
    price_basis: PriceBasis
    sale_basis: Sales
    core_charge: Decimal | None = Field(gt=0)
    # Exact text supporting the price. Code checks it appears in the source email;
    # a valid schema does not prove the model copied it faithfully.
    price_phrase: str | None

class QuoteWrapper(BaseModel):
    quote_list: list[Quote]

def ask_model(
    quote_text: str,
    system_prompt: str = SYSTEM_PROMPT_V1,
    response_model: type[BaseModel] = Quote,
) -> str:
    """Send the system prompt and the quote as separate messages; return the raw reply text.

    Only the request differs per machine: LM Studio on the Mac, Ollama on Linux.
    """
    if OS_NAME == "Darwin":
        model = lms.llm(LLM_MODEL)
        chat = lms.Chat(system_prompt)
        chat.add_user_message(quote_text)
        result = model.respond(chat, response_format=response_model.model_json_schema())
        return result.content

    client = Client(host=LLM_MODEL_HOST, timeout=TIMEOUT)
    response: ChatResponse = client.chat(
        model=LLM_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': quote_text},
        ],
        think=True,
        stream=False,
        format=response_model.model_json_schema()
    )
    return response.message.content


def extract_quotes(email_text: str) -> list[Quote]:
    """Extract every offer in one email with SYSTEM_PROMPT_V2.

    Returns:
        The validated quotes (empty if the email makes no offer).

    Raises:
        pydantic.ValidationError: the reply does not match QuoteWrapper.
        httpx.TimeoutException / ollama.ResponseError: transport failures.
    """
    start = time.perf_counter()
    raw = ask_model(email_text, SYSTEM_PROMPT_V2, QuoteWrapper)
    logger.info(
        "model call model=%s prompt=%s latency=%.1fs",
        LLM_MODEL, PROMPT_VERSION, time.perf_counter() - start,
    )
    return QuoteWrapper.model_validate_json(raw).quote_list


def main():
    validation_failures = 0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # 1. Get a reply. Failures here are transport/server problems, not the model's output.
        try:
            raw = ask_model(quote)
        except ConnectionError:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: model server not reachable at {LLM_MODEL_HOST}.")
        except httpx.TimeoutException:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: no response within {TIMEOUT}s (server reachable, generation too slow).")
        except lms.LMStudioError as err:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: LM Studio request failed ({type(err).__name__}): {err}")
        except (ResponseError, ValidationError) as err:
            # ollama raises ResponseError for HTTP errors, and a pydantic ValidationError
            # when the server's reply isn't a chat response at all (e.g. a wrong API route).
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: server replied with an error instead of a chat message:\n{err}")
        else:
            # 2. Check the model's output against the Quote schema.
            print("RAW:", raw)
            try:
                quote_result = Quote.model_validate_json(raw)
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
