import logging
import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import httpx
import lmstudio as lms
from ollama import ChatResponse, Client, ResponseError
from pydantic import BaseModel, Field, ValidationError

from config import LLM_MODEL, LLM_MODEL_HOST, OS_NAME

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
# V3 (lesson 4.4): three one-line rule changes, each tuned on a dev case only.
#   E21 (dev twin of held-out E18): an in-stock item without a price is still an offer.
#   E22 (dev twin of held-out E13): keep any stated currency code, not only USD/EUR.
#   E01: a condition belongs to one offer; do not copy it to another offer in the email.
SYSTEM_PROMPT_V3 = """You extract offers from aircraft-parts supplier emails.
Return {"quote_list": [...]} with one record per offer the buyer could accept on its own.
If the email makes no offer (e.g. no stock), return an empty quote_list.
A part that is in stock is an offer even if no price is given: return it with price null.

Rules:
- Only use values that appear in the email. Never guess. If a field is not stated, use null.
- part_number: exactly as written.
- quantity: units in stock now; do not count units in repair or available later.
- condition: OH = overhauled, SV = serviceable (incl. "Inspected/Tested"), NE = new.
  As-removed, untested, or not stated -> null.
  Use only the condition stated for this offer; never copy it from another offer in the email.
- currency: the ISO code exactly as stated (e.g. USD, EUR, GBP, CAD); null if no currency is stated.
- price: the number as a plain decimal (e.g. 3.450,00 -> 3450.00); null if no price is stated.
- price_basis: PER_UNIT if the price is per unit/each, LOT if it is a total for all units.
- sale_basis: OUTRIGHT or EXCHANGE. For exchanges, price is the exchange fee.
- core_charge: the amount owed if an exchange core is not returned; null for outright offers.
- price_phrase: copy the exact words from the email that state the price, character for character.
  null if no price is stated.
"""
PROMPT_VERSION = "V3"
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

@dataclass(frozen=True)
class ModelReply:
    """The model's reply text plus the measurements needed to compare models.

    Fields a provider does not report stay None rather than being guessed.
    """
    content: str
    model: str
    provider: str  # "ollama", "lmstudio", or "anthropic"
    input_tokens: int | None = None
    output_tokens: int | None = None  # Ollama: eval_count, which includes thinking tokens
    generation_s: float | None = None  # time spent generating output (Ollama eval_duration)
    thinking_chars: int | None = None  # length of returned thinking text, when the provider returns it

    @property
    def tokens_per_s(self) -> float | None:
        """Output tokens per second of generation, or None if either number is missing."""
        if not self.output_tokens or not self.generation_s:
            return None
        return self.output_tokens / self.generation_s


def is_hosted(llm_model: str) -> bool:
    """True for models served by the hosted Anthropic API rather than a local server."""
    return llm_model.startswith("claude-")


def ask_model(
    quote_text: str,
    system_prompt: str = SYSTEM_PROMPT_V1,
    response_model: type[BaseModel] = Quote,
    llm_model: str = LLM_MODEL,
    timeout: float = TIMEOUT,
) -> ModelReply:
    """Send the system prompt and the quote as separate messages; return the reply and its stats.

    The provider is chosen by model name: "claude-*" goes to the Anthropic API;
    anything else goes to LM Studio on the Mac or Ollama on Linux.

    Raises:
        httpx.TimeoutException (Ollama) / anthropic.APITimeoutError: no reply within `timeout`.
        ollama.ResponseError / anthropic.APIStatusError: the server answered with an error.
    """
    if is_hosted(llm_model):
        return _ask_anthropic(quote_text, system_prompt, response_model, llm_model, timeout)

    if OS_NAME == "Darwin":
        model = lms.llm(llm_model)
        chat = lms.Chat(system_prompt)
        chat.add_user_message(quote_text)
        result = model.respond(chat, response_format=response_model.model_json_schema())
        return ModelReply(content=result.content, model=llm_model, provider="lmstudio")

    client = Client(host=LLM_MODEL_HOST, timeout=timeout)
    response: ChatResponse = client.chat(
        model=llm_model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': quote_text},
        ],
        think=True,
        stream=False,
        format=response_model.model_json_schema()
    )
    thinking = response.message.thinking
    return ModelReply(
        content=response.message.content,
        model=llm_model,
        provider="ollama",
        input_tokens=response.prompt_eval_count,
        output_tokens=response.eval_count,
        generation_s=response.eval_duration / 1e9 if response.eval_duration else None,
        thinking_chars=len(thinking) if thinking is not None else None,
    )


def _ask_anthropic(
    quote_text: str,
    system_prompt: str,
    response_model: type[BaseModel],
    llm_model: str,
    timeout: float,
) -> ModelReply:
    """Call the Anthropic Messages API with structured output constrained to response_model.

    Reads the key from ANTHROPIC_API_KEY (or an `ant auth login` profile); never from code.
    The SDK retries 429/5xx/connection errors itself; capped at 2 retries here.
    """
    import anthropic  # imported here so local-only runs do not need the hosted SDK

    client = anthropic.Anthropic(timeout=timeout, max_retries=2)
    response = client.messages.parse(
        model=llm_model,
        max_tokens=16000,
        system=system_prompt,
        messages=[{"role": "user", "content": quote_text}],
        output_format=response_model,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"{llm_model} refused the request: {response.stop_details}")
    # Return the raw JSON text so the same QuoteWrapper validation runs for every provider.
    text = next(b.text for b in response.content if b.type == "text")
    return ModelReply(
        content=text,
        model=llm_model,
        provider="anthropic",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def extract_quotes_with_reply(
    email_text: str, llm_model: str = LLM_MODEL, timeout: float = TIMEOUT
) -> tuple[list[Quote], ModelReply]:
    """Extract every offer in one email with SYSTEM_PROMPT_V3; also return the raw reply and stats.

    Raises:
        pydantic.ValidationError: the reply does not match QuoteWrapper.
        Transport errors from ask_model (timeouts, server errors).
    """
    start = time.perf_counter()
    reply = ask_model(email_text, SYSTEM_PROMPT_V3, QuoteWrapper, llm_model, timeout)
    tps = reply.tokens_per_s
    logger.info(
        "model call model=%s provider=%s prompt=%s latency=%.1fs in_tokens=%s out_tokens=%s "
        "thinking_chars=%s tok_per_s=%s",
        reply.model, reply.provider, PROMPT_VERSION, time.perf_counter() - start,
        reply.input_tokens, reply.output_tokens, reply.thinking_chars,
        f"{tps:.1f}" if tps else None,
    )
    return QuoteWrapper.model_validate_json(reply.content).quote_list, reply


def extract_quotes(email_text: str, llm_model: str = LLM_MODEL, timeout: float = TIMEOUT) -> list[Quote]:
    """Extract every offer in one email with SYSTEM_PROMPT_V3.

    Returns:
        The validated quotes (empty if the email makes no offer).

    Raises:
        pydantic.ValidationError: the reply does not match QuoteWrapper.
        httpx.TimeoutException / ollama.ResponseError: transport failures.
    """
    quotes, _ = extract_quotes_with_reply(email_text, llm_model, timeout)
    return quotes


def main():
    validation_failures = 0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # 1. Get a reply. Failures here are transport/server problems, not the model's output.
        try:
            raw = ask_model(quote).content
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
