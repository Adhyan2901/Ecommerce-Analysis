import re

# Keywords that should never appear in a query we're about to execute.
# This blocks writes/schema changes even if they show up disguised
# inside a subquery, CTE name, or comment.
FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", "truncate",
    "create", "grant", "revoke", "exec", "execute", "call",
    "copy", "vacuum", "reindex", "cluster",
]


class UnsafeSQLError(Exception):
    pass


def validate_sql(sql: str) -> str:
    """Raise UnsafeSQLError if the SQL is anything other than a single
    read-only SELECT statement. Returns the cleaned SQL if safe."""

    cleaned = sql.strip().rstrip(";").strip()

    if not cleaned:
        raise UnsafeSQLError("Empty query generated.")

    # Must start with SELECT or WITH (a CTE that ends in a SELECT)
    first_word = cleaned.split(None, 1)[0].lower()
    if first_word not in ("select", "with"):
        raise UnsafeSQLError(
            f"Query must start with SELECT or WITH, got: '{first_word}'"
        )

    # Reject multiple statements (anything with a semicolon in the middle)
    if ";" in cleaned:
        raise UnsafeSQLError("Multiple statements are not allowed.")

    # Reject any forbidden keyword, as a whole word (so 'update' doesn't
    # false-positive match inside a column name like 'updated_at')
    lowered = cleaned.lower()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", lowered):
            raise UnsafeSQLError(f"Forbidden keyword detected: '{kw}'")

    return cleaned


def add_limit_if_missing(sql: str, default_limit: int = 1000) -> str:
    """Add a LIMIT clause if the query doesn't already have one, so a
    mistaken query can't try to return millions of rows."""
    if re.search(r"\blimit\s+\d+", sql, re.IGNORECASE):
        return sql
    return f"{sql}\nLIMIT {default_limit}"


if __name__ == "__main__":
    # Quick tests
    good = "SELECT * FROM orders WHERE order_status = 'delivered'"
    bad_1 = "DROP TABLE orders"
    bad_2 = "SELECT * FROM orders; DROP TABLE orders"
    bad_3 = "UPDATE orders SET order_status = 'delivered'"

    print(validate_sql(good))
    print(add_limit_if_missing(good))

    for bad in (bad_1, bad_2, bad_3):
        try:
            validate_sql(bad)
            print(f"FAILED TO CATCH: {bad}")
        except UnsafeSQLError as e:
            print(f"Correctly blocked: {e}")