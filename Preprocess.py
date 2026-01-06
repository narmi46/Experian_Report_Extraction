import streamlit as st
import pdfplumber
import re
import json
import tempfile
import os


# -------------------------------
# Helper Functions
# -------------------------------

def extract_company_name(filename):
    """
    Extract company name from PDF filename
    Example: 'LARNEY SDN. BHD. (3) 2.pdf' → 'LARNEY SDN. BHD.'
    """
    name = os.path.basename(filename)
    name = re.sub(r"\(.*?\)", "", name)   # remove brackets
    name = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)
    return name.strip()


def read_all_pages(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append({
                    "page_number": idx + 1,
                    "text": text
                })
    return pages


def extract_litigation_section(pages):
    collecting = False
    collected_text = []
    found_pages = []

    for page in pages:
        text = page["text"]

        if re.search(r"SECTION\s+3:\s+LITIGATION INFORMATION", text, re.IGNORECASE):
            collecting = True

        if collecting:
            collected_text.append(text)
            found_pages.append(page["page_number"])

        if collecting and re.search(r"SECTION\s+4:", text, re.IGNORECASE):
            break

    return "\n".join(collected_text), found_pages


def determine_suit_role(company_name, window_text):
    company = company_name.upper()

    plaintiff_block = re.search(r"Plaintiff\s+(.+?)\s+(Defendant|Local No)", window_text, re.DOTALL)
    defendant_block = re.search(r"Defendant\s+(.+?)\s+(Local No|Case Status)", window_text, re.DOTALL)

    if plaintiff_block and company in plaintiff_block.group(1).upper():
        return "PLAINTIFF"

    if defendant_block and company in defendant_block.group(1).upper():
        return "DEFENDANT"

    return "UNKNOWN"


def parse_legal_suits(litigation_text, company_name):
    cases = []

    case_numbers = re.finditer(
        r"(BK-[A-Z0-9\-\/]+-\d{4})",
        litigation_text
    )

    for match in case_numbers:
        case = {"case_no": match.group(1)}

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

        # 🔥 Suit role
        case["company_role"] = determine_suit_role(company_name, window)

        cases.append(case)

    return cases


# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Litigation Extractor", layout="wide")
st.title("⚖️ Litigation Information Extractor")

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:
    company_name = extract_company_name(uploaded_file.name)
    st.info(f"🏢 **Company Detected:** {company_name}")

    with st.spinner("Processing PDF..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        pages = read_all_pages(pdf_path)
        litigation_text, litigation_pages = extract_litigation_section(pages)

    if not litigation_text:
        st.error("❌ Litigation section not found.")
    else:
        st.success(f"✅ Litigation section found on pages: {litigation_pages}")

        legal_cases = parse_legal_suits(litigation_text, company_name)

        if not legal_cases:
            st.info("ℹ️ No legal cases found.")
        else:
            st.subheader(f"📌 Total Legal Cases Found: {len(legal_cases)}")

            for i, case in enumerate(legal_cases, 1):
                role = case.get("company_role", "UNKNOWN")
                emoji = "🟢" if role == "PLAINTIFF" else "🔴" if role == "DEFENDANT" else "⚪"

                with st.expander(f"{emoji} Case {i}: {case['case_no']} ({role})"):
                    st.json(case)

            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(legal_cases, indent=2),
                file_name="legal_suits_output.json",
                mime="application/json"
            )

            with st.expander("🧾 Raw Litigation Text"):
                st.text(litigation_text)
