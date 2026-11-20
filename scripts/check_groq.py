"""Check that your Groq API key works.

Run:  uv run python scripts/check_groq.py

It lists the models your key can use, then asks one model a short question.
"""

import os

from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq

load_dotenv()  # reads GROQ_API_KEY and GROQ_MODEL from the .env file

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing. Put it in the .env file.")

client = Groq(api_key=api_key)
models = sorted(model.id for model in client.models.list().data)
print(f"Your key can use {len(models)} models:")
for name in models:
    print(f"  {name}")

model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
print(f"\nAsking {model_name} a question...")
llm = ChatGroq(model=model_name, temperature=0)
reply = llm.invoke("In one sentence: what is a GSTIN?")
print(reply.content)
