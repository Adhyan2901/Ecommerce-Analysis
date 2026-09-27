import matplotlib.pyplot as plt
import pandas as pd


def make_chart(df: pd.DataFrame, question: str):
    """Pick a chart type based on the shape of the DataFrame and return
    a matplotlib figure, or None if the data doesn't suit a chart."""

    if df is None or df.empty:
        return None

    n_rows, n_cols = df.shape

    # Single value (e.g. "how many canceled orders?") -> no chart, just the number
    if n_rows == 1 and n_cols == 1:
        return None

    # Try to find a date/time-like column and a numeric column -> line chart
    date_col = next((c for c in df.columns if "date" in c.lower() or "month" in c.lower() or "day" in c.lower()), None)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if date_col and numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df[date_col], df[numeric_cols[0]], marker="o")
        ax.set_title(question)
        ax.set_xlabel(date_col)
        ax.set_ylabel(numeric_cols[0])
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    # Otherwise, if there's one categorical column and one numeric column -> bar chart
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    if categorical_cols and numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        plot_df = df.head(15)  # avoid an unreadable chart with 100+ bars
        ax.barh(plot_df[categorical_cols[0]], plot_df[numeric_cols[0]])
        ax.set_title(question)
        ax.set_xlabel(numeric_cols[0])
        ax.invert_yaxis()  # largest value at the top
        plt.tight_layout()
        return fig

    # Data doesn't fit a chart shape we recognize
    return None


if __name__ == "__main__":
    # Quick manual test with fake data shaped like real query results
    monthly = pd.DataFrame({
        "month": pd.date_range("2017-01-01", periods=6, freq="MS"),
        "revenue": [127482, 271239, 414330, 390812, 566851, 490050],
    })
    categories = pd.DataFrame({
        "category": ["health_beauty", "watches_gifts", "bed_bath_table"],
        "revenue": [1407759, 1261539, 1224602],
    })
    single = pd.DataFrame({"canceled_orders": [580]})

    for name, df in [("monthly", monthly), ("categories", categories), ("single", single)]:
        fig = make_chart(df, f"Test: {name}")
        print(f"{name}: {'chart created' if fig else 'no chart (as expected)' if name == 'single' else 'NO CHART — unexpected!'}")
        if fig:
            fig.savefig(f"test_{name}.png")
            print(f"  saved to test_{name}.png")