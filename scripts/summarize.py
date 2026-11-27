import lmstudio as lms

from quote_assistant.config import BASE_DIR, LLM_MODEL

EMAIL_PATH = BASE_DIR / "data" / "sample_email.txt"
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

email = read_email(EMAIL_PATH)
model = lms.llm(LLM_MODEL)
chat = lms.Chat(SUMMARY_PROMPT_V1)
chat.add_user_message(email)
result = model.respond(chat, config={
    "temperature": 0.6
})
print(result)