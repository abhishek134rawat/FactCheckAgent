import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import os

# ---------------- LOAD ENV ----------------
load_dotenv()
st.write(os.getenv("OPENAI_API_KEY"))
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("Fact Check Agent")


# ---------------- WEB SEARCH ----------------
def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return " ".join([r["body"] for r in results])


# ---------------- FILE UPLOAD ----------------
pdf = st.file_uploader("Upload PDF", type="pdf")
claims = ""
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

    # ---------------- STEP 1: EXTRACT CLAIMS ----------------
    if st.button("Extract Claims with AI"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Extract factual claims from this text.
                    Return only bullet points.
                    {text}  """
                }
                ]
        )

        claims = response.choices[0].message.content
        st.subheader("📌 AI Extracted Claims")
        st.write(claims)

    # ---------------- STEP 2: VERIFY CLAIMS ----------------
    if st.button("Verify Claims"):
        if not claims:
            st.warning("Please extract claims first!")
        else:
            st.subheader("🔍 Fact Check Results")
            for claim in claims.split("\n"):
                claim = claim.strip()
                if claim:
                    web_data = web_search(claim)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {   "role": "user",
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

                    st.write("### 🧾 Claim")
                    st.write(claim)

                    st.write("### 📊 Result")
                    st.write(result)

                    st.write("---")