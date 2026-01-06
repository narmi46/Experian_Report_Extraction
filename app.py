import streamlit as st
import pandas as pd

st.set_page_config(page_title="CTOS Parameters by Bank", layout="wide")

st.title("📊 CTOS Parameters (4)")
st.caption("Bank-Specific Classification (from CTOS Policy)")

# -----------------------------
# Bank Selection
# -----------------------------
banks = [
    "RHB Bank",
    "Maybank",
    "CIMB Bank",
    "Standard Chartered",
    "SME Bank",
    "Bank Rakyat"
]

selected_bank = st.selectbox("Select Bank", banks)
st.divider()

# -----------------------------
# CTOS Bank-Specific Mapping
# -----------------------------
CTOS_MAPPING = {
    "RHB Bank": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Strict 2"),
        ("Legal Status on Loan", "Strict 2"),
    ],
    "Maybank": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Not Applicable"),
        ("Legal Status on Loan", "Strict 2"),
    ],
    "CIMB Bank": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Strict 2"),
        ("Legal Status on Loan", "Strict 2"),
    ],
    "Standard Chartered": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Preference"),
        ("Legal Status on Loan", "Strict 2"),
    ],
    "SME Bank": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Strict 2"),
        ("Legal Status on Loan", "Strict 2"),
    ],
    "Bank Rakyat": [
        ("No Legal Suits at All", "Preference"),
        ("Any Legal Suits", "Strict 2"),
        ("Trade Bureau", "Strict 2"),
        ("Legal Status on Loan", "Strict 2"),
    ],
}

# -----------------------------
# Build Table
# -----------------------------
def build_ctos_table(bank):
    rows = []
    for param, param_type in CTOS_MAPPING[bank]:
        rows.append({
            "Parameter": param,
            "Type": param_type,
            "Criteria": "",
            "Status": "",
            "Detail": ""
        })
    return pd.DataFrame(rows)

# -----------------------------
# Display
# -----------------------------
st.subheader(f"🏦 {selected_bank} — CTOS Parameters")

df = build_ctos_table(selected_bank)

st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.info(
    "ℹ️ Parameter Type is bank-specific (from CTOS policy).\n\n"
    "Criteria, Status, and Detail are intentionally left empty.\n\n"
    "Next step: plug in legal suit extraction & evaluation logic."
)
