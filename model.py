from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel

class Quote(BaseModel):
    part_number: str
    quantity: int
    condition: str
    currency: str
    unit_price: float
    sale_basis: str

response: ChatResponse = chat(
    model='qwen3.5:9b',
    messages=[
        {
            'role': 'user',
            'content': 'Is the sky blue?'
        }],
    think=True,
    stream=False,
    format=Quote.model_json_schema()
)

response = Quote(part_number="TRAIN-PN-001", quantity=2, condition="overhauled",
      currency="USD", unit_price="1250.00", sale_basis="exchange")

print(response)