WINDOW = """o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp < '2018-09-01'"""

EVAL_SET = [
    {
        "id": 1,
        "question": "How many orders were delivered?",
        "reference_sql": f"SELECT COUNT(*) FROM orders o WHERE o.order_status = 'delivered' AND {WINDOW}",
        "expect": "answer",
    },
    {
        "id": 2,
        "question": "How many orders were canceled?",
        "reference_sql": f"SELECT COUNT(*) FROM orders o WHERE o.order_status = 'canceled' AND {WINDOW}",
        "expect": "answer",
    },
    {
        "id": 3,
        "question": "What is the total revenue?",
        "reference_sql": f"""SELECT SUM(oi.price + oi.freight_value)
            FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.order_status = 'delivered' AND {WINDOW}""",
        "expect": "answer",
    },
    {
        "id": 4,
        "question": "How many customers ordered more than once?",
        "reference_sql": f"""SELECT COUNT(*) FROM (
                SELECT c.customer_unique_id
                FROM orders o JOIN customers c ON c.customer_id = o.customer_id
                WHERE o.order_status = 'delivered' AND {WINDOW}
                GROUP BY c.customer_unique_id HAVING COUNT(o.order_id) > 1) t""",
        "expect": "answer",
    },
    {
        "id": 5,
        "question": "Who is the president of Brazil?",
        "reference_sql": None,
        "expect": "refuse",
    },
]