import streamlit as st

st.set_page_config(page_title="Olist Analytics Assistant", page_icon="📊")

st.title("📊 E-commerce Analytics Assistant")
st.caption(
    "Ask a business question about the Olist e-commerce dataset "
    "(orders, customers, products, sellers, payments, reviews)."
)

try:
    from pipeline import ask
except Exception as e:
    st.error(f"Could not load the assistant: {type(e).__name__}: {e}")
    st.stop()

with st.expander("Example questions you can ask"):
    st.markdown(
        "- What is total revenue by month?\n"
        "- Which product category has the most orders?\n"
        "- How many customers ordered more than once?\n"
        "- What is the average order value by payment method?\n"
        "- Which states have the most canceled orders?"
    )

question = st.text_input("Your question:", placeholder="e.g. What was total revenue in 2018?")
submitted = st.button("Ask", type="primary")

if submitted and not question.strip():
    st.warning("Please type a question first.")

if submitted and question.strip():
    with st.spinner("Thinking..."):
        result = ask(question)

    if not result.success:
        st.warning(result.error)
        if result.sql:
            with st.expander("Generated SQL (blocked or failed)"):
                st.code(result.sql, language="sql")
    else:
        st.subheader("Insight")
        st.write(result.insight)

        if result.chart is not None:
            st.subheader("Chart")
            st.pyplot(result.chart)

        st.subheader("Data")
        st.dataframe(result.data)

        with st.expander("View the SQL query that was run"):
            st.code(result.sql, language="sql")