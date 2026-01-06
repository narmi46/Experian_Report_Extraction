import streamlit as st
import pdfplumber
import re
import json
import tempfile


# --------------------------------
# Helpers
# --------------------------------

def read_all_pages(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append({
                    "page_number": i + 1,
                    "text": text
                })
    return pages


def extract_company_name(pages):
    for page in pages[:3]:
        text = page["text"]

        m1 = re.search(r"Name Of Subject\s+([A-Z\s\.&]+)", text)
        if m1:
            return m1.group(1).strip()

        m2 = re.search(r"Company Name\s+([A-Z\s\.&]+)", text)
        if m2:
            return m2.group(1).strip()

    return "UNKNOWN COMPANY"


# --------------------------------
# 🔥 MULTI SECTION 3 EXTRACTION
# --------------------------------

def extract_all_litigation_sections(pages):
    sections = []
    collecting = False
    buffer = []
    pages_buffer = []
    role = "UNKNOWN"

    for page in pages:
        text = page["text"]

        # START new Section 3
        if re.search(r"SECTION\s+3:\s+LITIGATION INFORMATION", text, re.I):
            if buffer:
                sections.append({
                    "text": "\n".join(buffer),
                    "pages": pages_buffer,
                    "role": role
                })

            collecting = True
            buffer = [text]
            pages_buffer = [page["page_number"]]
            role = "UNKNOWN"

            if "SUBJECT AS DEFENDANT" in text.upper():
                role = "DEFENDANT"
            elif "SUBJECT AS PLAINTIFF" in text.upper():
                role = "PLAINTIFF"

            continue

        if collecting:
            buffer.append(text)
            pages_buffer.append(page["page_number"])

            if "SUBJECT AS DEFENDANT" in text.upper():
                role = "DEFENDANT"
            elif "SUBJECT AS PLAINTIFF" in text.upper():
                role = "PLAINTIFF"

            # END this Section 3
            if re.search(r"SECTION\s+4:", text, re.I):
                sections.append({
                    "text": "\n".join(buffer),
                    "pages": pages_buffer,
                    "role": role
                })
                collecting = False
                buffer = []
                pages_buffer = []
                role = "UNKNOWN"

    # Catch trailing section
    if buffer:
        sections.append({
            "text": "\n".join(buffer),
            "pages": pages_buffer,
            "role": role
        })

    return sections


# --------------------------------
# Case Parsing
# --------------------------------

def parse_legal_suits(litigation_text, role):
    cases = []

    case_numbers = re.finditer(
        r"(BK-[A-Z0-9\-\/]+-\d{4})",
        litigation_text
    )

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
st.title("⚖️ Litigation Information Extractor")

uploaded_file = st.file_uploader("📄 Upload Experian / CTOS PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    # 🔄 Loading Indicator
    with st.spinner("Processing PDF, please wait..."):
        pages = read_all_pages(pdf_path)
        company_name = extract_company_name(pages)
        sections = extract_all_litigation_sections(pages)

    # 🏢 Company Title
    st.markdown(f"# 🏢 {company_name}")
    st.markdown("## ⚖️ Litigation Information")

    if not sections:
        st.warning("No Litigation Sections Found.")
        st.stop()

    all_cases = []

    for idx, section in enumerate(sections, 1):
        cases = parse_legal_suits(section["text"], section["role"])

        for case in cases:
            case["section_no"] = idx
            case["section_pages"] = section["pages"]

        all_cases.extend(cases)

        st.markdown(f"### 📄 Section {idx} (Pages {section['pages']})")
        st.info(f"Company Role: **{section['role']}**")

        if not cases:
            st.warning("No cases found in this section.")
        else:
            for i, case in enumerate(cases, 1):
                emoji = "🔴" if case["company_role"] == "DEFENDANT" else "🟢"
                with st.expander(f"{emoji} Case {i}: {case['case_no']}"):
                    st.json(case)

    st.subheader(f"📌 Total Legal Cases Found: {len(all_cases)}")

    st.download_button(
        "💾 Download JSON",
        json.dumps(all_cases, indent=2),
        file_name="legal_suits_output.json",
        mime="application/json"
    )
