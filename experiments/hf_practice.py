import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


token_test = ["2117A0000-01", "12500.00", "OH", "OUTRIGHT", "Price is USD 9,850.00 each, outright."]
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
input_ids = []
token_ids = []
for pt in token_test:
    input_ids.append(tokenizer.encode(pt))
print(f"encoded input_ids: {input_ids}")
for n in input_ids:
    token_ids.append(tokenizer.convert_ids_to_tokens(n))
print(f"id to strings: {token_ids}")
decoded_input_ids = tokenizer.decode(input_ids)
print(f"decoded input_ids: {decoded_input_ids}")

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")