import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = genai.list_models()

model_name = None
for m in models:
    if "generateContent" in m.supported_generation_methods:
        model_name = m.name
        break

if model_name is None:
    st.error("No Gemini model available")
    st.stop()

model = genai.GenerativeModel(model_name)

st.set_page_config(page_title="Fact Check Agent", layout="wide")
st.title("📄 Fact Check Agent (AI Powered)")

pdf = st.file_uploader("Upload PDF", type="pdf")

if pdf:

    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    st.subheader("📌 Extracted Text")
    st.text_area("PDF Content", text, height=250)

    if st.button("🚀 Analyze Claims"):

        with st.spinner("Analyzing with AI..."):

            prompt = f"""
You are a fact-checking assistant.

Extract factual claims from the text.

For each claim:
- classify: Likely True / Needs Verification / Possibly False
- give confidence score (0-100)
- short reason

Text:
{text[:12000]}
"""

            response = model.generate_content(prompt)
            output = response.text

            st.subheader("🧠 Fact Check Results")
            st.markdown(output)

            st.success("Analysis Completed!")