import streamlit as st
import requests

st.title("Resume ATS Checker")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    files = {"file": uploaded_file.getvalue()}
    
    with st.spinner("Processing..."):
        response = requests.post("http://127.0.0.1:5000/upload", files={"file": uploaded_file})
    
    if response.status_code == 200:
        data = response.json()
        
        st.subheader("ATS Score:")
        st.progress(data["ats_score"] / 100)
        st.write(f"**Score:** {data['ats_score']}%")

        st.subheader("Missing Keywords:")
        st.write(", ".join(data["missing_keywords"]) if data["missing_keywords"] else "✅ No missing keywords!")

        st.subheader("Missing Sections:")
        st.write(", ".join(data["missing_sections"]) if data["missing_sections"] else "✅ All necessary sections are present!")

        st.subheader("Sentence Feedback:")
        for feedback in data["sentence_feedback"]:
            st.warning(feedback)
    else:
        st.error('Error processing resume.')
