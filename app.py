import streamlit as st
import pandas as pd

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="CTOS Bank Assessment",
    layout="wide"
)

st.title("📊 CTOS Parameters (4)")
st.caption("Bank-Specific Evaluation • Dynamic Status Engine")

# =====================================================
# Bank Selection
# =====================================================
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

# =====================================================
# CTOS POLICY (STATIC — NEVER PUT STATUS HERE)
# =====================================================
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

# =====================================================
# MOCK CTOS EXTRACTION RESULT (REPLACE WITH PDF OUTPUT)
# =====================================================
ctos_result = {
    "legal_suits_count": 0,
    "defendant_cases": 0,
    "trade_bureau_outstanding": 0,
    "legal_action_on_loan": False,
}

# =====================================================
# EVALUATION ENGINE (DYNAMIC)
# =====================================================
def evaluate_ctos_parameter(bank, parameter, param_type, ctos):
    # Handle Not Applicable
    if param_type == "Not Applicable":
        return "N/A", "N/A", ""

    if parameter == "No Legal Suits at All":
        if ctos["legal_suits_count"] == 0:
            return "Pass", "No legal suits found", ""
        return "Fail", "Legal suits detected", ""

    if parameter == "Any Legal Suits":
        if ctos["defendant_cases"] == 0:
            return "Pass", "No defendant cases", ""
        return "Fail", "Defendant legal cases present", ""

    if parameter == "Trade Bureau":
        if ctos["trade_bureau_outstanding"] == 0:
            return "Pass", "No trade bureau records", ""
        return "Conditional", "Outstanding trade bureau record", ""

    if parameter == "Legal Status on Loan":
        if not ctos["legal_action_on_loan"]:
            return "Pass", "No legal action on existing loan", ""
        return "Fail", "Legal action detected on loan", ""

    return "", "", ""

# =====================================================
# TABLE BUILDER
# =====================================================
def build_ctos_table(bank, ctos):
    rows = []

    for parameter, param_type in CTOS_MAPPING[bank]:
        status, criteria, detail = evaluate_ctos_parameter(
            bank, parameter, param_type, ctos
        )

        rows.append({
            "Parameter": parameter,
            "Type": param_type,
            "Criteria": criteria,
            "Status": status,
            "Detail": detail
        })

    return pd.DataFrame(rows)

# =====================================================
# DISPLAY
# =====================================================
st.subheader(f"🏦 {selected_bank} — CTOS Parameters")

df = build_ctos_table(selected_bank, ctos_result)

st.dataframe(df, use_container_width=True, hide_index=True)

# =====================================================
# EXPLANATION
# =====================================================
st.divider()
st.info(
    "ℹ️ **How this works**\n\n"
    "- Bank policy (Type) is static\n"
    "- Status & Criteria are dynamically evaluated\n"
    "- No array modification required\n"
    "- Ready to plug in PDF extraction output\n\n"
    "**Next upgrades**:\n"
    "- Plaintiff vs Defendant logic\n"
    "- 1-year / 2-year settlement rules\n"
    "- Strict 2 grade cascade\n"
    "- KreditLab HTML badge styling"
)
