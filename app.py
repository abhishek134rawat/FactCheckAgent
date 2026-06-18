import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Extract factual claims from the text below.

Return only bullet points.

{text[:12000]}
"""
                    }
                ]
            )

            claims = response.choices[0].message.content

            st.subheader("AI Extracted Claims")
            st.write(claims)