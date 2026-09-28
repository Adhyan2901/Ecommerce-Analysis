import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from schema_context import SCHEMA_CONTEXT

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Tried in order. If the first is overloaded, the next one is used.
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash"]


def generate_sql(question: str, max_retries: int = 4) -> str:
    """Send a business question to Gemini and get back a SQL query.
    Returns None if the question isn't answerable from this database.
    Retries with growing waits, then falls back to the next model."""
    prompt = f"{SCHEMA_CONTEXT}\n\nQ: \"{question}\"\nA:\n"
    last_error = None

    for model in MODELS:
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                sql = response.text.strip()
                sql = re.sub(r"^```sql\s*|\s*```$", "", sql, flags=re.MULTILINE).strip()

                if sql == "NOT_ANSWERABLE":
                    return None
                return sql

            except errors.ServerError as e:
                last_error = e
                if attempt < max_retries:
                    wait = 3 * attempt  # 3s, 6s, 9s
                    print(f"  ({model} busy, retrying in {wait}s... attempt {attempt}/{max_retries})")
                    time.sleep(wait)
            except errors.ClientError as e:
                # e.g. model name not available: skip to the next model
                last_error = e
                break

    raise last_error


if __name__ == "__main__":
    for q in ["What is total revenue by month?", "How many customers ordered more than once?"]:
        print(f"\nQ: {q}\n{'-' * 50}")
        print(generate_sql(q))