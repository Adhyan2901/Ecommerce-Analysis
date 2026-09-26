import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from schema_context import SCHEMA_CONTEXT

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_sql(question: str, max_retries: int = 3) -> str:
    """Send a business question to Gemini and get back a SQL query.
    Retries automatically if the model is temporarily overloaded (503)."""
    prompt = f"{SCHEMA_CONTEXT}\n\nQ: \"{question}\"\nA:\n"

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            sql = response.text.strip()
            sql = re.sub(r"^```sql\s*|\s*```$", "", sql, flags=re.MULTILINE).strip()
            return sql

        except errors.ServerError as e:
            if attempt == max_retries:
                raise
            wait = 2 ** attempt  # 2s, 4s, 8s
            print(f"  (model busy, retrying in {wait}s... attempt {attempt}/{max_retries})")
            time.sleep(wait)


if __name__ == "__main__":
    test_questions = [
        "What is total revenue by month?",
        "Which product category has the most orders?",
        "How many customers ordered more than once?",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        print("-" * 50)
        print(generate_sql(q))
        print()