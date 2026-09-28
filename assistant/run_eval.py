import time
import pandas as pd
from google.genai import errors
from eval_set import EVAL_SET
from query_generator import generate_sql
from db_executor import run_query
from sql_safety import validate_sql, UnsafeSQLError


def norm_cell(x):
    if hasattr(x, "isoformat"):
        return x.isoformat()[:10]
    try:
        return str(round(float(x), 1))
    except (TypeError, ValueError):
        return str(x)


def to_rows(df):
    return [[norm_cell(c) for c in row] for row in df.itertuples(index=False)]


def results_match(ref_df, got_df):
    """Same number of rows, and every reference value appears in the matching
    assistant row. Ignores column names, order, and extra columns."""
    ref_rows, got_rows = to_rows(ref_df), to_rows(got_df)
    if len(ref_rows) != len(got_rows):
        return False
    unused = list(got_rows)
    for ref in ref_rows:
        found = next((g for g in unused if all(v in g for v in ref)), None)
        if found is None:
            return False
        unused.remove(found)
    return True


def evaluate(item):
    """Returns (status, detail, sql). status is PASS, FAIL, or ERROR.
    ERROR = the model was unavailable, so the question could not be judged."""
    sql = ""
    try:
        sql = generate_sql(item["question"])
        if item["expect"] == "refuse":
            if sql is None:
                return "PASS", "", ""
            try:
                validate_sql(sql)
                return "FAIL", "should have been refused but a query was produced", sql
            except UnsafeSQLError:
                return "PASS", "blocked by the safety layer", sql
        if sql is None:
            return "FAIL", "refused a valid question", ""
        got = run_query(sql)
        ref = run_query(item["reference_sql"])
        if results_match(ref, got):
            return "PASS", "", sql
        return "FAIL", "result differs from reference", sql
    except errors.ServerError as e:
        return "ERROR", f"model unavailable: {e.code}", sql
    except Exception as e:
        return "FAIL", f"{type(e).__name__}: {e}", sql


results = {}
pending = list(EVAL_SET)

for pass_number in range(1, 4):
    if not pending:
        break
    if pass_number > 1:
        print(f"\n--- Pass {pass_number}: retrying {len(pending)} unanswered question(s) after a 60s pause ---")
        time.sleep(60)

    still_pending = []
    for item in pending:
        status, detail, sql = evaluate(item)
        print(f"[{status}] #{item['id']} {item['question']}  {detail}")
        if status == "ERROR":
            still_pending.append(item)
        results[item["id"]] = {"id": item["id"], "question": item["question"],
                               "status": status, "detail": detail, "generated_sql": sql}
        time.sleep(8)  # stay under the free-tier rate limit
    pending = still_pending

df = pd.DataFrame(results.values()).sort_values("id")
df.to_csv("eval_results.csv", index=False)

answered = df[df["status"] != "ERROR"]
passed = (answered["status"] == "PASS").sum()
errors_left = (df["status"] == "ERROR").sum()

print("\n" + "=" * 50)
print(f"Answered by the model: {len(answered)} of {len(df)}")
print(f"Passed: {passed}/{len(answered)} = {100 * passed / max(len(answered), 1):.0f}%")
if errors_left:
    print(f"{errors_left} question(s) never got a response (Gemini busy). Rerun later to complete them.")