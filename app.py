import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("Fact Check Agent")

pdf = st.file_uploader("Upload PDF", type="pdf")

# 🌐 Web search
def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return " ".join([r["body"] for r in results])

if pdf:

    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    st.subheader("Extracted Text")
    st.text_area("", text, height=200)

    if st.button("Fact Check Now"):
        # STEP 1: Extract claims
        claim_prompt = f""" 
        Extract only factual claims (numbers, dates, stats, facts).
        Text:
        {text[:12000]}
        """
        try:
            claims = model.generate_content(claim_prompt).text
        except:
            claims = ""
  
        st.subheader(" Claims Found")
        st.write(claims)

        st.subheader("🔍 Verification Results")

        # STEP 2: Check each claim
        for claim in claims.split("\n"):

            if claim.strip():

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

Rules:
- If fact matches latest info → Correct (Updated)
- If fact is true but old → Correct but Outdated
- If no proof or wrong → Incorrect / False

Also give 1 line reason.
"""

                try:
                    result = model.generate_content(verify_prompt).text
                except:
                    result = "API limit reached"

                st.markdown("### Claim")
                st.write(claim)

                st.markdown("### Verdict")
                st.write(result)

                st.markdown("---")