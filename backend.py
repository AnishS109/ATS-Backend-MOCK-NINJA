from flask import Flask, request, jsonify
import io
from pdfminer.high_level import extract_text
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Comprehensive keyword list
keywords = ["python", "machine learning", "data science", "sql", "react", "django", "java", "deep learning", "api",
            "aws", "tensorflow", "nlp"]

# Resume sections expected
sections = ["education", "experience", "projects", "skills", "certifications", "summary"]

# Extract text from PDF
def extract_resume_text(pdf_file):
    pdf_stream = io.BytesIO(pdf_file.read())  # Convert file to BytesIO
    return extract_text(pdf_stream)

# Calculate ATS score
def calculate_ats_score(resume_text):
    clean_text = re.sub(r'[^\w\s]', '', resume_text.lower())  # Remove punctuation

    # Count keyword matches using word boundaries
    keyword_match = sum(1 for word in keywords if re.search(r'\b' + re.escape(word) + r'\b', clean_text))
    keyword_score = (keyword_match / len(keywords)) * 50

    # Section matching (checks presence of section headers)
    section_match = sum(1 for sec in sections if re.search(r'\b' + re.escape(sec) + r'\b', clean_text))
    section_score = (section_match / len(sections)) * 20

    # Keyword frequency bonus (caps at 15 points)
    keyword_frequency = sum(clean_text.count(word) for word in keywords)
    frequency_score = min((keyword_frequency / len(keywords)) * 15, 15)

    # Formatting score (Assume perfect formatting)
    formatting_score = 15

    # Final ATS score calculation
    ats_score = keyword_score + section_score + frequency_score + formatting_score
    return round(min(ats_score, 100), 2), keyword_match, section_match, clean_text

# Sentence analysis for improvements
def analyze_sentences(resume_text):
    feedback = []
    sentences = [sentence.strip() for sentence in resume_text.split('.') if sentence.strip()]

    for sentence in sentences:
        words = sentence.split()
        
        # Check for short sentences
        if len(words) < 8:
            feedback.append(f"Short Sentence: Expand this - '{sentence}'")
        
        # Encourage adding metrics (numbers)
        if not any(char.isdigit() for char in sentence):
            feedback.append(f"Add Metrics: Consider adding numbers - '{sentence}'")
        
        # Check for weak action verbs
        weak_phrases = ["worked on", "responsible for", "helped with"]
        if any(phrase in sentence.lower() for phrase in weak_phrases):
            feedback.append(f"Use Stronger Verbs: Rephrase this - '{sentence}'")

        # Detect passive voice
        if re.search(r"\bwas\b|\bwere\b|\bbeen\b|\bbeing\b", sentence.lower()):
            feedback.append(f"Passive Voice: Consider active voice - '{sentence}'")

    return feedback

# Flask Route to Upload Resume
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty file uploaded"}), 400
    
    try:
        resume_text = extract_resume_text(file)
    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500

    if not resume_text.strip():
        return jsonify({"error": "No extractable text found in resume"}), 500
    
    # Perform analysis
    ats_score, keyword_match, section_match, clean_text = calculate_ats_score(resume_text)
    sentence_feedback = analyze_sentences(resume_text)

    missing_keywords = [word for word in keywords if re.search(r'\b' + re.escape(word) + r'\b', clean_text) is None]
    missing_sections = [sec for sec in sections if re.search(r'\b' + re.escape(sec) + r'\b', clean_text) is None]

    return jsonify({
        "ats_score": ats_score,
        "keyword_match": keyword_match,
        "section_match": section_match,
        "missing_keywords": missing_keywords,
        "missing_sections": missing_sections,
        "sentence_feedback": sentence_feedback
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # Prevent multi-threading issues
