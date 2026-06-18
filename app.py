import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("Fact Check Agent")

pdf = st.file_uploader(
    "Upload PDF",
    type="pdf"
)

if pdf:

    reader = PdfReader(pdf)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    st.subheader("Extracted Text")
    st.text_area("PDF Content", text, height=250)

    if st.button("Extract Claims with AI"):

        with st.spinner("Analyzing..."):

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