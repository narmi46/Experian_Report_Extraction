import streamlit as st
import pandas as pd

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="CTOS Parameters",
    layout="wide"
)

st.title("📊 CTOS Parameters (4)")
st.caption("Foundation Table — Criteria & Result To Be Applied Later")

# -----------------------------
# Bank Selector (1 at a time)
# -----------------------------
banks = [
    "RHB Bank",
    "Maybank",
    "CIMB Bank",
    "Standard Chartered",
    "SME Bank",
    "Bank Rakyat"
]

selected_bank = st.selectbox(
    "Select Bank",
    banks
)

st.divider()

# -----------------------------
# CTOS Parameters (4) — Base Structure
# -----------------------------
def get_ctos_parameters_table():
    data = [
        {
            "Parameter": "No Legal Suits at All",
            "Type": "Preference",
            "Criteria": "",
            "Status": "",
            "Detail": ""
        },
        {
            "Parameter": "Legal Suit (Defendant)",
            "Type": "Strict 2",
            "Criteria": "",
            "Status": "",
            "Detail": ""
        },
        {
            "Parameter": "Trade Bureau",
            "Type": "Strict 2",
            "Criteria": "",
            "Status": "",
            "Detail": ""
        },
        {
            "Parameter": "Legal Status on Loan",
            "Type": "Strict 2",
            "Criteria": "",
            "Status": "",
            "Detail": ""
        }
    ]

    return pd.DataFrame(data)

# -----------------------------
# Display Table
# -----------------------------
st.subheader(f"🏦 {selected_bank} — CTOS Parameters")

ctos_df = get_ctos_parameters_table()

st.dataframe(
    ctos_df,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Placeholder Note
# -----------------------------
st.divider()
st.info(
    "ℹ️ Criteria, Status, and Detail are intentionally left blank.\n\n"
    "Next phase:\n"
    "- Inject CTOS / Experian extraction results\n"
    "- Apply bank-specific criteria\n"
    "- Auto-evaluate Pass / Fail / Conditional\n"
    "- Match HTML grading logic"
)
