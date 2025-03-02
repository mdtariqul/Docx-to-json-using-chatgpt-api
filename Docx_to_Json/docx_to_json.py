import streamlit as st
import openai
import os
from dotenv import load_dotenv
from docx import Document
import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_docx_content(docx_file):
    """Extract text from a .docx file."""
    document = Document(docx_file)
    full_text = []
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)

def extract_resume_to_json(resume_text):
    """Extract relevant fields from a resume and return them in JSON format."""
    prompt = f"""
You are a resume parsing assistant. Extract the following information from the resume text and return it in JSON format:

- Name
- Contact Information (Phone, Email, Address)
- Summary or Objective
- Work Experience (Company, Role, Dates, Responsibilities)
- Education (Institution, Degree, Field of Study, Dates)
- Skills
- Certifications
- Projects

Resume Text:
\"\"\"
{resume_text}
\"\"\"

Ensure your response is valid JSON.
"""
    st.write(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that provides JSON outputs only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0
    )

    reply = response['choices'][0]['message']['content']

    try:
        parsed_data = json.loads(reply)
        return parsed_data
    except json.JSONDecodeError:
        st.error("Failed to parse the resume response. Please try again.")
        return None

def display_evaluation(evaluation, document_type):
    st.write(f"## {document_type} Evaluation Results")

    scores = evaluation.get("scores", {})
    comments = evaluation.get("comments", {})

    st.write("### Scores:")
    for criterion, score in scores.items():
        st.write(f"- **{criterion}**: {score}/5")

    st.write("### Comments:")
    for criterion, comment in comments.items():
        st.write(f"- **{criterion}**: {comment}")

def main():
    st.title("Extract information in Json format")

    st.write("## Upload Your Documents")

    resume_file = st.file_uploader("Upload your Resume (.docx):", type="docx")

    if st.button("Evaluate Documents"):
        if  not resume_file:
            st.error("Please provide at least one document to evaluate.")
        else:           
            with st.spinner("Parsing Resume..."):
                resume_text = extract_docx_content(resume_file)
                resume_json = extract_resume_to_json(resume_text)
                if resume_json:
                    st.write("## Resume Parsed Data")
                    st.json(resume_json)

if __name__ == "__main__":
    main()
