import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
from google.api_core.exceptions import ResourceExhausted

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Get model
models = genai.list_models()
model_name = None

for m in models:
    if "generateContent" in m.supported_generation_methods:
        model_name = m.name
        break

model = genai.GenerativeModel(model_name)

# UI setup
st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("📄 AI Fact Check Agent")


# ---------------- SAFE GEMINI FUNCTION ----------------
def safe_generate(prompt):
    try:
        return model.generate_content(prompt).text
    except ResourceExhausted:
        time.sleep(2)
        return "⚠️ API limit reached, try again later"


# ---------------- WEB SEARCH ----------------
@st.cache_data
def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return " ".join([r["body"] for r in results])


# ---------------- FILE UPLOAD ----------------
pdf = st.file_uploader("Upload PDF", type="pdf")

if pdf:

    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    text = text[:8000]  # LIMIT TEXT SIZE

    st.subheader("📌 Extracted Text")
    st.text_area("", text, height=200)

    if st.button("🚀 Fact Check Now"):

        # STEP 1: Extract claims
        claim_prompt = f"""
Extract only factual claims (numbers, dates, stats, facts).

Text:
{text}
"""

        claims = safe_generate(claim_prompt)

        st.subheader("📌 Claims Found")
        st.write(claims)

        # convert claims to list
        claims_list = [c.strip("-• ") for c in claims.split("\n") if len(c.strip()) > 5]

        st.subheader("🔍 Verification Results")

        # STEP 2: check claims (LIMITED)
        for claim in claims_list[:5]:

            web_data = web_search(claim)

            verify_prompt = f"""
You are a strict fact-checking AI.

Claim: {claim}

Web Evidence:
{web_data}

Classify into ONLY ONE:
1. Correct (Updated)
2. Correct but Outdated
3. Incorrect / False

Also give 1 line reason.
"""

            result = safe_generate(verify_prompt)

            st.markdown("### 🧾 Claim")
            st.write(claim)

            st.markdown("### 📊 Verdict")
            st.write(result)

            st.markdown("---")

            time.sleep(1)  # avoid rate limit