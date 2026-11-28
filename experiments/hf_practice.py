import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

token_test = ["2117A0000-01", "12500.00", "OH", "OUTRIGHT", "Price is USD 9,850.00 each, outright."]
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

# Step 1: token ids per string (plain lists, different lengths)
input_ids = []
token_ids = []
for pt in token_test:
    input_ids.append(tokenizer.encode(pt))
print(f"encoded input_ids: {input_ids}")
for n in input_ids:
    token_ids.append(tokenizer.convert_ids_to_tokens(n))
print(f"id to strings: {token_ids}")
print(f"decoded input_ids: {[tokenizer.decode(ids) for ids in input_ids]}")

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

# Step 2: one string as a batch-of-1 tensor
sentence = token_test[-1]
inputs = tokenizer(sentence, return_tensors="pt")
print(f"input_ids tensor: {inputs['input_ids']}")
print(f"input_ids shape: {inputs['input_ids'].shape}")

# Fix for the original line: keep the tensor in a variable, then ask it for its shape
t = torch.tensor(input_ids[-1])
print(f"t shape: {t.shape}")

with torch.no_grad():
    outputs = model(**inputs)
print(outputs.logits.shape)
print(model.config.vocab_size)

next_id = outputs.logits[0, -1].argmax()
print(tokenizer.decode(next_id))

q1 = tokenizer(["OH", "2117A0000-01"], return_tensors="pt", padding=True)
print(q1)