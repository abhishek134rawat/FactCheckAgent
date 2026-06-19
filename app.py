import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
from google.api_core.exceptions import ResourceExhausted

# ---------------- SETUP ----------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("📄 Fact Check Agent")


# ---------------- SAFE GEMINI ----------------
def safe_generate(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return ""


# ---------------- WEB SEARCH ----------------
@st.cache_data
def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=2)
        return " ".join([r["body"] for r in results])


# ---------------- UI ----------------
pdf = st.file_uploader("Upload PDF", type="pdf")

if pdf:

    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    text = text[:6000]   # keep small (IMPORTANT)

    st.text_area("Extracted Text", text, height=200)

    if st.button("Run Fact Check 🚀"):

        # ✅ STEP 1: ONE SIMPLE CALL (IMPORTANT FIX)
        prompt = f"""
Extract 5 factual claims from this text in bullet points:

{text}

Return only bullets.
"""

        claims = safe_generate(prompt)

        st.subheader("Claims")

        st.write(claims)

        # clean claims
        claims_list = [c.strip("-• ") for c in claims.split("\n") if len(c.strip()) > 5]

        st.subheader("Verification")

        # ✅ LIMIT 5 CLAIMS ONLY
        for claim in claims_list[:5]:

            web_data = web_search(claim)

            verify_prompt = f"""
Fact check this:

Claim: {claim}

Evidence:
{web_data}

Answer in 3 lines:
- Verdict (Correct / Incorrect / Outdated)
- Reason
"""

            result = safe_generate(verify_prompt)

            st.markdown("### Claim")
            st.write(claim)

            st.markdown("### Result")
            st.write(result)

            st.markdown("---")

            time.sleep(1)
            