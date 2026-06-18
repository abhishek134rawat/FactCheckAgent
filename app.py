import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🔥 FIX: dynamically pick working model
models = genai.list_models()

model_name = None
for m in models:
    if "generateContent" in m.supported_generation_methods:
        model_name = m.name
        break

if model_name is None:
    st.error("No Gemini model found")
    st.stop()

model = genai.GenerativeModel(model_name)

st.title("📄 Fact Check Agent")
# Upload PDF
pdf = st.file_uploader("Upload PDF", type="pdf")

if pdf:

    # Read PDF
    reader = PdfReader(pdf)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    st.subheader("Extracted Text")
    st.text_area("PDF Content", text, height=250)

    # Button click
    if st.button("Extract Claims with AI"):

        with st.spinner("Analyzing with Gemini AI..."):

            try:
                response = model.generate_content(
                    f"""
Extract factual claims from the text below.

Return only bullet points.

{text[:12000]}
"""
                )

                claims = response.text

                st.subheader("AI Extracted Claims")
                st.write(claims)

            except Exception as e:
                st.error(f"Error occurred: {e}")