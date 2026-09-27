import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import pandas as pd

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

INSIGHT_PROMPT = """You are a data analyst writing a short summary for a
business audience. You will be given a business question and the actual
query results that answer it (as a small table).

Write a 2-3 sentence plain-English insight. Rules:
- Use ONLY numbers that appear in the data below. Never invent, estimate,
  or round in a way that changes the meaning.
- Do not describe the table structure (e.g. don't say "the table shows
  columns for..."). Just state the finding.
- If there's an obvious trend, standout value, or comparison worth
  noting, mention it. Otherwise just summarize what the numbers say.
- No markdown, no bullet points, plain sentences only.

Question: {question}

Data ({n_rows} rows total, showing up to 20):
{data_preview}
"""


def generate_insight(question: str, data: pd.DataFrame, max_retries: int = 3) -> str:
    """Generate a plain-English insight from query results.
    Returns a fallback message if generation fails (never crashes)."""

    if data is None or data.empty:
        return "No data was returned for this question."

    preview = data.head(20).to_string(index=False)
    prompt = INSIGHT_PROMPT.format(
        question=question,
        n_rows=len(data),
        data_preview=preview,
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            return response.text.strip()

        except errors.ServerError:
            if attempt == max_retries:
                return "(Insight generation is temporarily unavailable — see the table above for the results.)"
            wait = 2 ** attempt
            time.sleep(wait)
        except Exception:
            return "(Couldn't generate an insight for this result — see the table above.)"


if __name__ == "__main__":
    test_df = pd.DataFrame({
        "month": ["2017-09-01", "2017-10-01", "2017-11-01", "2017-12-01"],
        "revenue": [701077.49, 751117.01, 1153364.20, 843078.29],
    })

    insight = generate_insight("What is total revenue by month?", test_df)
    print(insight)