import streamlit as st
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# API KEY
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Auto model selection
models = genai.list_models()
model_name = None

for m in models:
    if "generateContent" in m.supported_generation_methods:
        model_name = m.name
        break

model = genai.GenerativeModel(model_name)

st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("📄 The Fact-Check Agent")
st.write("Upload PDF → Extract Claims → Verify via Web → Get Truth Score")

# PDF Upload
pdf = st.file_uploader("Upload PDF", type="pdf")

# Web search function
def web_search(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(r["body"])
    return " ".join(results)

if pdf:

    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    st.subheader("📌 Extracted Text")
    st.text_area("PDF Content", text, height=250)

    if st.button("🚀 Run Fact Check"):

        with st.spinner("Extracting claims..."):

            claim_prompt = f"""
Extract ONLY factual claims (numbers, dates, stats, financial info) from this text:

{text[:12000]}

Return as bullet points.
"""

            claims = model.generate_content(claim_prompt).text

        st.subheader("📌 Extracted Claims")
        st.write(claims)

        st.subheader("🔍 Verification Report")

        final_prompt = ""

        for claim in claims.split("\n"):

            if claim.strip():

                search_data = web_search(claim)

                verify_prompt = f"""
You are a strict fact checker.

Claim: {claim}

Web Evidence:
{search_data}

Classify:
- Verified (matches real data)
- Inaccurate (conflicts with real data)
- False (no evidence found)

Also give short reason.
"""

                response = model.generate_content(verify_prompt)

                st.markdown("### 🧾 Claim")
                st.write(claim)

                st.markdown("### 📊 Result")
                st.write(response.text)

                st.markdown("---")