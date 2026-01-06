# app.py
# Streamlit app: CTOS Parameters (4) + Experian PDF upload
# MVP scope:
# - Upload Experian report (PDF)
# - Parse ONLY "Legal Suits" total count
# - Evaluate ONLY RHB Bank → Parameter 1 ("No Legal Suits at All")
# - Fill Status + Detail (string) for that row only

import re
import pandas as pd
import streamlit as st
import pdfplumber


# =========================
# UI CONFIG
# =========================
st.set_page_config(page_title="CTOS + Experian Parser (MVP)", layout="wide")
st.title("📊 CTOS Parameters (4) — Bank View")
st.caption("MVP: Upload Experian PDF → Auto-fill RHB Parameter 1 (Status + Detail)")


# =========================
# BANK + POLICY + CRITERIA (STATIC)
# (Criteria differs by bank, based on your screenshots)
# =========================
BANKS = [
    "RHB Bank",
    "Maybank",
    "CIMB Bank",
    "Standard Chartered",
    "SME Bank",
    "Bank Rakyat",
]

CTOS_MAPPING = {
    "RHB Bank": [
        ("No Legal Suits at All", "Preference", "No legal suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance defendant"),
        ("Trade Bureau", "Strict 2", ">RM5k needs approval"),
        ("Legal Status on Loan", "Strict 2", "Require settlement"),
    ],
    "Maybank": [
        ("No Legal Suits at All", "Preference", "No suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance"),
        ("Trade Bureau", "Not Applicable", "N/A"),
        ("Legal Status on Loan", "Strict 2", "Settlement"),
    ],
    "CIMB Bank": [
        ("No Legal Suits at All", "Preference", "No suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance"),
        ("Trade Bureau", "Strict 2", "With settlement"),
        ("Legal Status on Loan", "Strict 2", "Settlement"),
    ],
    "Standard Chartered": [
        ("No Legal Suits at All", "Preference", "No suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance"),
        ("Trade Bureau", "Preference", "Approval possible"),
        ("Legal Status on Loan", "Strict 2", "Settlement"),
    ],
    "SME Bank": [
        ("No Legal Suits at All", "Preference", "No suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance"),
        ("Trade Bureau", "Strict 2", "Settlement/arrangement"),
        ("Legal Status on Loan", "Strict 2", "Settlement"),
    ],
    "Bank Rakyat": [
        ("No Legal Suits at All", "Preference", "No suits"),
        ("Legal Suit (Defendant)", "Strict 2", "Zero tolerance"),
        ("Trade Bureau", "Strict 2", "Settlement/arrangement"),
        ("Legal Status on Loan", "Strict 2", "Settlement"),
    ],
}


# =========================
# PARSER (Experian PDF → facts)
# =========================
def parse_experian_legal_suits_count(uploaded_pdf_file) -> dict:
    """
    Extract total Legal Suits count from an Experian PDF.
    Returns a dict of facts (not UI strings):
      {"legal_suits_count": int, "debug_match": str|None}
    """
    full_text = ""

    with pdfplumber.open(uploaded_pdf_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

    # Typical pattern in Experian summary: "Legal Suits 3"
    m = re.search(r"Legal\s+Suits\s+(\d+)", full_text, re.IGNORECASE)
    if m:
        return {"legal_suits_count": int(m.group(1)), "debug_match": m.group(0)}

    # Fallback: sometimes line breaks split words; try a looser match
    m2 = re.search(r"Legal\s*Suits[\s:]*?(\d+)", full_text, re.IGNORECASE)
    if m2:
        return {"legal_suits_count": int(m2.group(1)), "debug_match": m2.group(0)}

    # If not found, return 0 but flag that it was not detected
    return {"legal_suits_count": 0, "debug_match": None}


# =========================
# RULE (Bank logic) — MVP only: RHB Parameter 1
# =========================
def evaluate_rhb_parameter_1(experian_facts: dict) -> dict:
    """
    RHB Param 1: No Legal Suits at All
    Return UI strings for Status + Detail.
    """
    count = experian_facts.get("legal_suits_count", 0)
    if count == 0:
        return {
            "status": "Pass",
            "detail": "No legal suits detected from Experian report (Legal Suits = 0).",
        }
    return {
        "status": "Fail",
        "detail": f"Legal suits detected from Experian report (Legal Suits = {count}).",
    }


# =========================
# TABLE BUILDER
# =========================
def build_ctos_table(bank: str, rhb_param1_result: dict | None) -> pd.DataFrame:
    """
    Build the CTOS Parameters (4) table for the selected bank.
    - Criteria filled from CTOS_MAPPING
    - Status + Detail:
        - N/A rows => Status=N/A, Detail=""
        - RHB Param 1 => filled if rhb_param1_result is provided
        - others empty for now
    """
    rows = []
    for idx, (parameter, param_type, criteria) in enumerate(CTOS_MAPPING[bank], start=1):
        status = ""
        detail = ""

        # Not Applicable rows (Maybank Trade Bureau)
        if param_type == "Not Applicable":
            status = "N/A"
            detail = ""

        # MVP injection: ONLY RHB + Parameter 1
        if bank == "RHB Bank" and parameter == "No Legal Suits at All" and rhb_param1_result:
            status = rhb_param1_result["status"]
            detail = rhb_param1_result["detail"]

        rows.append(
            {
                "#": idx,
                "Parameter": parameter,
                "Type": param_type,
                "Criteria": criteria,
                "Status": status,
                "Detail": detail,
            }
        )

    return pd.DataFrame(rows)


# =========================
# SIDEBAR / INPUTS
# =========================
with st.sidebar:
    st.header("Inputs")
    selected_bank = st.selectbox("Select Bank", BANKS)

    uploaded_file = st.file_uploader(
        "Upload Experian Report (PDF)",
        type=["pdf"],
        help="MVP: used to fill RHB Parameter 1 only",
    )

    show_debug = st.checkbox("Show debug (parsed facts)", value=False)


# =========================
# PROCESS UPLOAD (MVP)
# =========================
rhb_param1_result = None
experian_facts = None

if uploaded_file is not None:
    with st.spinner("Parsing Experian PDF..."):
        experian_facts = parse_experian_legal_suits_count(uploaded_file)

    # Evaluate only if bank is RHB (MVP scope)
    if selected_bank == "RHB Bank":
        with st.spinner("Evaluating RHB Parameter 1..."):
            rhb_param1_result = evaluate_rhb_parameter_1(experian_facts)

    if show_debug:
        st.sidebar.subheader("Debug")
        st.sidebar.write("Parsed facts:", experian_facts)
        st.sidebar.write("RHB param1 result:", rhb_param1_result)


# =========================
# MAIN OUTPUT
# =========================
st.subheader(f"🏦 {selected_bank} — CTOS Parameters (4)")
df = build_ctos_table(selected_bank, rhb_param1_result)

st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.info(
    "✅ MVP behavior:\n"
    "- Upload Experian PDF\n"
    "- App parses total **Legal Suits** count\n"
    "- Only **RHB Bank → Parameter 1** is evaluated and filled (Status + Detail)\n"
    "- Other parameters remain blank for now\n"
    "- Maybank Trade Bureau remains **N/A**\n\n"
    "Next step (when you’re ready): parse defendant/plaintiff + case status and fill Parameter 2, 3, 4."
)
