import os
import time
import pandas as pd
from google.genai import errors
from eval_set import EVAL_SET
from query_generator import generate_sql
from db_executor import run_query
from sql_safety import validate_sql, UnsafeSQLError

RESULTS_FILE = "eval_results.csv"


class DailyQuotaExhausted(Exception):
    pass


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
    """Returns (status, detail, sql). PASS/FAIL judge the assistant.
    ERROR means the model was unavailable, so the question is not judged."""
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
    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg and "PerDay" in msg:
            raise DailyQuotaExhausted()
        if "RESOURCE_EXHAUSTED" in msg or "UNAVAILABLE" in msg or "503" in msg:
            return "ERROR", f"model unavailable: {type(e).__name__}", sql
        return "FAIL", f"{type(e).__name__}: {msg[:150]}", sql


def save(results):
    pd.DataFrame(results.values()).sort_values("id").to_csv(RESULTS_FILE, index=False)


# Load earlier progress, keeping only questions that were genuinely judged.
results = {}
if os.path.exists(RESULTS_FILE):
    old = pd.read_csv(RESULTS_FILE).fillna("")
    for r in old.to_dict("records"):
        detail = str(r["detail"])
        judged = r["status"] == "PASS" or (
            r["status"] == "FAIL"
            and "RESOURCE_EXHAUSTED" not in detail
            and "UNAVAILABLE" not in detail
        )
        if judged:
            results[int(r["id"])] = r

stopped = False
for pass_number in range(1, 4):
    pending = [i for i in EVAL_SET if results.get(i["id"], {}).get("status") in (None, "ERROR")]
    if not pending or stopped:
        break
    if pass_number > 1:
        print(f"\n--- Pass {pass_number}: retrying {len(pending)} question(s) after a 60s pause ---")
        time.sleep(60)

    for item in pending:
        try:
            status, detail, sql = evaluate(item)
        except DailyQuotaExhausted:
            print("\nDaily free-tier quota used up. Progress is saved. "
                  "Rerun tomorrow to finish the remaining questions.")
            stopped = True
            break
        print(f"[{status}] #{item['id']} {item['question']}  {detail}")
        results[item["id"]] = {"id": item["id"], "question": item["question"],
                               "status": status, "detail": detail, "generated_sql": sql}
        save(results)
        time.sleep(8)

judged = [r for r in results.values() if r["status"] in ("PASS", "FAIL")]
passed = sum(r["status"] == "PASS" for r in judged)
print("\n" + "=" * 50)
print(f"Judged so far: {len(judged)} of {len(EVAL_SET)} questions")
print(f"Passed: {passed}/{len(judged)} = {100 * passed / max(len(judged), 1):.0f}%")
if len(judged) < len(EVAL_SET):
    print(f"{len(EVAL_SET) - len(judged)} question(s) still to run. Rerun later.")