import pandas as pd
from query_generator import generate_sql
from db_executor import run_query
from sql_safety import UnsafeSQLError


class PipelineResult:
    """Holds everything about one question, so the UI can show all of it."""
    def __init__(self, question, sql=None, data=None, error=None):
        self.question = question
        self.sql = sql
        self.data = data
        self.error = error

    @property
    def success(self):
        return self.error is None


def ask(question: str) -> PipelineResult:
    """Full pipeline: question -> SQL -> validated -> executed -> DataFrame.
    Never raises; errors are captured in the result so the UI can display
    them gracefully instead of crashing."""

    # Step 1: generate SQL
    try:
        sql = generate_sql(question)
    except Exception as e:
        return PipelineResult(question, error=f"Couldn't generate SQL: {e}")

    if sql is None:
        return PipelineResult(
            question,
            error="This question doesn't seem related to the e-commerce data "
                  "I have access to (orders, customers, products, sellers, "
                  "payments, reviews). Try asking about revenue, orders, "
                  "categories, or customers instead."
        )

    # Step 2 + 3: validate and execute (validation happens inside run_query)
    try:
        data = run_query(sql)
    except UnsafeSQLError as e:
        return PipelineResult(question, sql=sql, error=f"Unsafe query blocked: {e}")
    except Exception as e:
        return PipelineResult(question, sql=sql, error=f"Query failed to run: {e}")

    return PipelineResult(question, sql=sql, data=data)


if __name__ == "__main__":
    test_questions = [
        "What is total revenue by month?",
        "How many orders were canceled?",
        "What is the capital of France?",  # off-topic, should fail gracefully
    ]

    for q in test_questions:
        print(f"\n{'=' * 60}")
        print(f"Q: {q}")
        print('=' * 60)

        result = ask(q)

        if result.success:
            print(f"\nSQL:\n{result.sql}")
            print(f"\nResult ({len(result.data)} rows):")
            print(result.data.head(10))
        else:
            print(f"\nFailed: {result.error}")
            if result.sql:
                print(f"Generated SQL was:\n{result.sql}")