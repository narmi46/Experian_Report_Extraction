import streamlit as st
import pdfplumber
import re
import json
import tempfile


# --------------------------------
# Extraction Helpers
# --------------------------------

def extract_company_name(pages):
    """
    Extract company name from:
    - 'Name Of Subject'
    - 'Company Name'
    """
    for page in pages[:3]:  # only first few pages needed
        text = page["text"]

        m1 = re.search(r"Name Of Subject\s+([A-Z\s\.&]+)", text)
        if m1:
            return m1.group(1).strip()

        m2 = re.search(r"Company Name\s+([A-Z\s\.&]+)", text)
        if m2:
            return m2.group(1).strip()

    return "UNKNOWN COMPANY"


def read_all_pages(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append({"page_number": i + 1, "text": text})
    return pages


def extract_litigation_section(pages):
    collecting = False
    content = []
    role = "UNKNOWN"
    found_pages = []

    for page in pages:
        text = page["text"]

        if re.search(r"SECTION\s+3:\s+LITIGATION INFORMATION", text, re.I):
            collecting = True

        if collecting:
            content.append(text)
            found_pages.append(page["page_number"])

            # detect role from section headers
            if "SUBJECT AS DEFENDANT" in text.upper():
                role = "DEFENDANT"
            if "SUBJECT AS PLAINTIFF" in text.upper():
                role = "PLAINTIFF"

        if collecting and re.search(r"SECTION\s+4:", text, re.I):
            break

    return "\n".join(content), found_pages, role


def parse_legal_suits(litigation_text, role):
    cases = []

    case_numbers = re.finditer(r"(BK-[A-Z0-9\-\/]+-\d{4})", litigation_text)

    for match in case_numbers:
        case = {
            "case_no": match.group(1),
            "company_role": role
        }

        start = max(match.start() - 400, 0)
        end = match.end() + 400
        window = litigation_text[start:end]

        court = re.search(r"(SESSIONS COURT\s+[A-Z]+)", window)
        plaintiff = re.search(r"Plaintiff\s+(.+?)\s+Local No", window, re.DOTALL)
        status = re.search(r"Case Status\s+([A-Z]+)", window)
        hearing = re.search(r"Hearing Date\s+(\d{1,2}\s+\w+\s+\d{4})", window)

        if court:
            case["court"] = court.group(1)

        if plaintiff:
            case["plaintiff"] = " ".join(plaintiff.group(1).split())

        if status:
            case["status"] = status.group(1)

        if hearing:
            case["hearing_date"] = hearing.group(1)

        cases.append(case)

    return cases


# --------------------------------
# Streamlit UI
# --------------------------------

st.set_page_config(page_title="Litigation Extractor", layout="wide")

uploaded_file = st.file_uploader("📄 Upload Experian / CTOS PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    # ✅ Option 2: Simple Spinner (Minimal)
    with st.spinner("Processing PDF, please wait..."):
        pages = read_all_pages(pdf_path)
        company_name = extract_company_name(pages)
        litigation_text, pages_found, role = extract_litigation_section(pages)

        if not litigation_text:
            st.error("❌ Litigation section not found.")
            st.stop()

        cases = parse_legal_suits(litigation_text, role)

    # 🔥 BIG TITLE
    st.markdown(f"# 🏢 {company_name}")
    st.markdown("## ⚖️ Litigation Information")

    st.success(f"Found on pages: {pages_found}")
    st.info(f"Company Role in Suits: **{role}**")

    st.subheader(f"📌 Total Cases Found: {len(cases)}")

    for i, case in enumerate(cases, 1):
        emoji = "🔴" if case["company_role"] == "DEFENDANT" else "🟢"
        with st.expander(f"{emoji} Case {i}: {case['case_no']}"):
            st.json(case)

    st.download_button(
        "💾 Download JSON",
        json.dumps(cases, indent=2),
        file_name="legal_suits_output.json",
        mime="application/json"
    )

    with st.expander("🧾 Raw Litigation Text"):
        st.text(litigation_text)
