from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
from decimal import Decimal
from enum import Enum

quote = """Hi,

Thanks for your RFQ. We can offer the following:

P/N: TRAIN-PN-004
Qty: 3 EA
Condition: Inspected/Tested, with tags from our repair station
Price: USD 14,625.00 total, outright sale
Lead time: Stock, ships same day

Regards,
Northwind Aero Spares"""

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

response: ChatResponse = chat(
    model='qwen3.5:9b', # Linux WorkStation
    # model='qwen/qwen3-14b', # Macbook WorkStation
    messages=[
        {
            'role': 'user',
            'content': quote
        }],
    think=True,
    stream=False,
    format=Quote.model_json_schema()
)

try:
    print("RAW:", response.message.content)
    quote_result = Quote.model_validate_json(response.message.content)
except ConnectionError:
    print("Model server not reachable at localhost:11434. Is Ollama running?")
finally:
    print("VALIDATED:", quote_result)