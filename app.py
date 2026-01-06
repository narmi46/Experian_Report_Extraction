import streamlit as st
import pandas as pd

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="CTOS Legal Assessment",
    layout="wide"
)

st.title("📊 CTOS Legal Suit Assessment")
st.caption("SME Credit Policy View (Bank-by-Bank)")

# -----------------------------
# Bank Selection
# -----------------------------
banks = [
    "RHB Bank (SME)",
    "Maybank (SME)",
    "CIMB Bank (SME)",
    "Standard Chartered (SME)",
    "SME Bank",
    "Bank Rakyat"
]

selected_bank = st.selectbox(
    "Select Bank",
    banks
)

st.divider()

# -----------------------------
# Base CTOS Result Table
# -----------------------------
def get_ctos_table(bank_name):
    """
    Base structure only.
    Logic & evaluation will be added later.
    """
    data = [
        {
            "Parameter": "Legal Suits",
            "Type": "CTOS",
            "Criteria": "No legal suits at all",
            "Status": "Preferred",
            "Detail": "Most preferred scenario"
        },
        {
            "Parameter": "Legal Suits",
            "Type": "CTOS",
            "Criteria": "Applicant as Plaintiff",
            "Status": "Conditional",
            "Detail": "Acceptable if no major monetary loss and status is known"
        },
        {
            "Parameter": "Legal Suits",
            "Type": "CTOS",
            "Criteria": "Applicant as Defendant (Settled)",
            "Status": "Strict",
            "Detail": "Requires full settlement with valid settlement letter"
        },
        {
            "Parameter": "Legal Suits",
            "Type": "CTOS",
            "Criteria": "Applicant as Defendant (Ongoing)",
            "Status": "Reject",
            "Detail": "Ongoing cases without settlement are not acceptable"
        },
        {
            "Parameter": "Trade Bureau",
            "Type": "CTOS",
            "Criteria": "Outstanding > RM5,000",
            "Status": "Mitigation Required",
            "Detail": "Settlement & higher-level approval required"
        },
        {
            "Parameter": "Trade Bureau",
            "Type": "CTOS",
            "Criteria": "Outstanding ≤ RM5,000",
            "Status": "Conditional",
            "Detail": "Mitigation may be sufficient"
        }
    ]

    return pd.DataFrame(data)


# -----------------------------
# Display Section
# -----------------------------
st.subheader(f"🏦 Bank Policy: {selected_bank}")

ctos_df = get_ctos_table(selected_bank)

st.dataframe(
    ctos_df,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Placeholder for Future Logic
# -----------------------------
st.divider()
st.info(
    "ℹ️ This is the base CTOS policy table.\n\n"
    "Next phase:\n"
    "- Map Experian / CTOS extracted results\n"
    "- Auto-evaluate Status per bank\n"
    "- Highlight Accept / Conditional / Reject\n"
    "- Add mitigation checklist"
)
