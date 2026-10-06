from eval_set import EVAL_SET
from db_executor import run_query

for item in EVAL_SET:
    if item["reference_sql"] is None:
        print(f"#{item['id']} refusal test (no SQL)")
        continue
    try:
        df = run_query(item["reference_sql"])
        print(f"#{item['id']} OK  {len(df)} row(s)  first row: {df.iloc[0].tolist()}")
    except Exception as e:
        print(f"#{item['id']} ERROR {type(e).__name__}: {str(e)[:120]}")