import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import os
import time
# ----------------LOAD ENV------------------------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY missing in environment variables!")
    st.stop()
client = OpenAI(api_key=api_key)
st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("Fact Check Agent")
# ----------------WEB SEARCH------------------------------------------------------------------
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            return " ".join([r["body"] for r in results])
    except:
        return ""
# ----------------FILE UPLOAD--------------------------------------------------------------
pdf = st.file_uploader("Upload PDF", type="pdf")
claims = []
if pdf:
    reader = PdfReader(pdf)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    text = text[:12000]
    st.subheader("📌 Extracted Text")
    st.text_area("PDF Content", text, height=250)
# ----------------EXTRACT CLAIMS----------------------------------------------------------------
    if st.button("Extract Claims with AI"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Extract factual claims from this text.
Return only bullet points.
{text}
"""
                }
            ]
        )
        claims_text = response.choices[0].message.content
        claims = claims_text.split("\n")
        st.subheader("AI Extracted Claims")
        st.write(claims_text)
# ----------------VERIFY CLAIMS ----------------
    if st.button("Verify Claims"):
        if not claims:
            st.warning("Please extract claims first!")
        else:
            st.subheader("🔍 Fact Check Results")
            for claim in claims[:5]:   # limit to avoid rate limit
                claim = claim.strip()
                if claim:
                    web_data = web_search(claim)
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"""
Fact check this claim:
Claim: {claim}
Web Evidence:
{web_data}
Give:
1. Verdict (Correct / Incorrect / Outdated)
2. 1 line reason
"""
                                }
                            ]
                        )
                        result = response.choices[0].message.content
                    except Exception as e:
                        result = "API Error / Rate Limit reached"
                    st.write("### Claim")
                    st.write(claim)
                    st.write("### Result")
                    st.write(result)
                    st.write("---")
                    time.sleep(1)  # avoid rate limit