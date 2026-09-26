import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

from sql_safety import validate_sql, add_limit_if_missing, UnsafeSQLError

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))


def run_query(sql: str, timeout_seconds: int = 10) -> pd.DataFrame:
    """Validate and execute a SQL query using the read-only connection.
    Raises UnsafeSQLError if the query fails validation."""

    safe_sql = validate_sql(sql)
    safe_sql = add_limit_if_missing(safe_sql)

    with engine.connect() as conn:
        # Statement timeout: if a query somehow runs too long
        # (bad join, huge scan), kill it instead of hanging forever.
        conn.execute(text(f"SET statement_timeout = {timeout_seconds * 1000}"))
        result = pd.read_sql(text(safe_sql), conn)

    return result


if __name__ == "__main__":
    # Test 1: a normal, safe query should work
    good_sql = """
        SELECT order_status, COUNT(*) AS orders
        FROM orders
        GROUP BY order_status
        ORDER BY orders DESC
    """
    print("Running a safe query:")
    print(run_query(good_sql))

    # Test 2: an unsafe query should be blocked BEFORE it reaches the DB
    print("\nAttempting an unsafe query:")
    try:
        run_query("DROP TABLE orders")
    except UnsafeSQLError as e:
        print(f"Correctly blocked before execution: {e}")

    # Test 3: even if validation somehow passed, the DB role itself
    # should refuse a write (defense in depth)
    print("\nTesting DB-level protection (bypassing our own validator):")
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM orders WHERE 1=0"))
    except Exception as e:
        print(f"Correctly blocked at the database level: {type(e).__name__}")