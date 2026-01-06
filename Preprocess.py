import streamlit as st
import pdfplumber
import re
import json
import tempfile


# -------------------------------
# PDF Processing Functions
# -------------------------------

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
    """
    Find SECTION 3: LITIGATION INFORMATION across ANY page
    and collect text until SECTION 4 starts.
    """
    collecting = False
    collected_text = []
    found_pages = []

    for page in pages:
        text = page["text"]

        # START
        if re.search(r"SECTION\s+3:\s+LITIGATION INFORMATION", text, re.IGNORECASE):
            collecting = True

        if collecting:
            collected_text.append(text)
            found_pages.append(page["page_number"])

        # STOP
        if collecting and re.search(r"SECTION\s+4:", text, re.IGNORECASE):
            break

    return "\n".join(collected_text), found_pages


def parse_legal_suits(litigation_text):
    cases = []

    case_numbers = re.finditer(
        r"(BK-[A-Z0-9\-\/]+-\d{4})",
        litigation_text
    )

    for match in case_numbers:
        case = {"case_no": match.group(1)}

        start = max(match.start() - 300, 0)
        end = match.end() + 300
        window = litigation_text[start:end]

        court = re.search(r"(SESSIONS COURT\s+[A-Z]+)", window)
        plaintiff = re.search(r"Plaintiff\s+(.+?)\s+Local No", window, re.DOTALL)
        status = re.search(r"Case Status\s+([A-Z]+)", window)
        hearing = re.search(
            r"Hearing Date\s+(\d{1,2}\s+\w+\s+\d{4})",
            window
        )

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


# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Litigation Extractor", layout="wide")

st.title("⚖️ Litigation Information Extractor")
st.write("Upload a **CTOS / company report PDF** to extract legal cases from **Section 3**.")

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        pages = read_all_pages(pdf_path)
        litigation_text, litigation_pages = extract_litigation_section(pages)

    if not litigation_text:
        st.error("❌ Litigation section not found.")
    else:
        st.success(f"✅ Litigation section found on pages: {litigation_pages}")

        legal_cases = parse_legal_suits(litigation_text)

        if not legal_cases:
            st.info("ℹ️ No legal cases found.")
        else:
            st.subheader(f"📌 Total Legal Cases Found: {len(legal_cases)}")

            for i, case in enumerate(legal_cases, 1):
                with st.expander(f"Case {i}: {case.get('case_no')}"):
                    st.json(case)

            # Download JSON
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(legal_cases, indent=2),
                file_name="legal_suits_output.json",
                mime="application/json"
            )

            # Optional: show raw litigation text
            with st.expander("🧾 Raw Litigation Text"):
                st.text(litigation_text)
