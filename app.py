import streamlit as st
import re
import spacy
import pdfplumber  # Used for reading PDFs
from docx import Document  # Used for reading DOCX files

#############################################
# 1. Define Skills Database and Field Mapping
#############################################

# SKILLS_DB: A list of skills to look for in resumes (both technical and non-technical)
SKILLS_DB = [
    # Technical Skills
    "python", "java", "c++", "sql", "machine learning", "data analysis",
    "tensorflow", "pytorch", "scikit-learn", "nlp", "deep learning",
    "html", "css", "javascript", "react", "angular", "node.js", "django", "flask",
    "aws", "azure", "gcp", "docker", "kubernetes", "cybersecurity", "data visualization",
    "software development", "api development", "cloud computing", "blockchain", "microservices",

    # Non-Technical / Soft Skills
    "communication", "project management", "leadership", "teamwork", "problem solving",
    "time management", "critical thinking", "creativity", "adaptability", "conflict resolution",
    "customer service", "sales", "marketing", "strategic planning", "negotiation",
    "budget management", "public speaking", "event planning", "human resources", "finance",
    "accounting", "research", "writing", "organization", "interpersonal skills"
]

# FIELD_SKILLS: Mapping between job fields and the specific skills required for that field.
FIELD_SKILLS = {
    "Computer Science": [
        "python", "java", "c++", "sql", "machine learning", "data analysis",
        "tensorflow", "pytorch", "scikit-learn", "nlp", "deep learning",
        "software development", "api development", "cloud computing"
    ],
    "Teaching": [
        "communication", "leadership", "teamwork", "time management",
        "critical thinking", "creativity", "curriculum development", "public speaking"
    ],
    "Marketing": [
        "communication", "strategic planning", "negotiation", "sales",
        "marketing", "digital marketing", "seo", "content creation", "social media"
    ],
    "Finance": [
        "accounting", "budget management", "financial analysis", "data analysis",
        "excel", "risk management", "finance"
    ],
    "Healthcare": [
        "patient care", "medical terminology", "communication", "empathy",
        "teamwork", "data analysis", "organization"
    ]
}

#############################################
# 2. Load and Cache spaCy Model
#############################################

@st.cache_resource
def load_nlp_model():
    """
    Load the spaCy language model and cache it.
    This function will be called only once per session.
    """
    try:
        return spacy.load("en_core_web_sm")
    except Exception as e:
        st.error("SpaCy model 'en_core_web_sm' not found. Install via: python -m spacy download en_core_web_sm")
        return None

nlp = load_nlp_model()
if not nlp:
    st.stop()

#############################################
# 3. File Reading Functions
#############################################

def read_pdf(file):
    """
    Extract text from a PDF file using pdfplumber.
    
    Parameters:
        file (UploadedFile): The PDF file uploaded by the user.
        
    Returns:
        text (str): The extracted text from the PDF.
    """
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def read_docx(file):
    """
    Extract text from a DOCX file using python-docx.
    
    Parameters:
        file (UploadedFile): The DOCX file uploaded by the user.
        
    Returns:
        text (str): The extracted text from the DOCX.
    """
    text = ""
    try:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
    return text

def read_txt(file):
    """
    Extract text from a TXT file.
    
    Parameters:
        file (UploadedFile): The TXT file uploaded by the user.
        
    Returns:
        text (str): The extracted text from the TXT file.
    """
    text = ""
    try:
        text = file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
    return text

#############################################
# 4. Extraction Functions
#############################################

def extract_emails(text):
    """
    Extract all email addresses from the text using a regular expression.
    
    Returns:
        List of email addresses.
    """
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(email_pattern, text)

def extract_phone_numbers(text):
    """
    Extract phone numbers from the text using a regular expression.
    The regex handles optional country codes, area codes, and common separators.
    
    Returns:
        List of phone numbers.
    """
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    return re.findall(phone_pattern, text)

def extract_name(text):
    """
    Extract the candidate's name from the resume text.
    Steps:
    1. Use spaCy NER to find PERSON entities and filter out those with digits.
    2. Return the first valid PERSON entity based on text position.
    3. If no valid entity is found, use a regex fallback for two or more capitalized words.
    
    Returns:
        Candidate name (str) or "Not found" if no name is detected.
    """
    doc_spacy = nlp(text)
    # Get candidate names with their start index, ignoring entities with digits.
    candidates = [(ent.start_char, ent.text) for ent in doc_spacy.ents
                  if ent.label_ == "PERSON" and not any(ch.isdigit() for ch in ent.text)]
    if candidates:
        candidates.sort(key=lambda x: x[0])  # sort by appearance in the text
        return candidates[0][1].strip()

    # Fallback regex: match two or more capitalized words (e.g., "John Doe")
    fallback_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
    matches = re.findall(fallback_pattern, text)
    if matches:
        return matches[0].strip()

    return "Not found"

def extract_skills(text):
    """
    Extract skills from the resume text.
    Compare each skill in SKILLS_DB with the text (case-insensitive) and return a deduplicated list.
    
    Returns:
        List of skills found in the resume.
    """
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    # Remove duplicates by converting to a set then back to list
    return list(set(found_skills))

def calculate_match_percentage(extracted_skills, required_skills):
    """
    Calculate the percentage match between the extracted skills from the resume and the required skills.
    
    Parameters:
        extracted_skills (list): Skills extracted from the resume.
        required_skills (list): Skills selected by the user from the sidebar.
    
    Returns:
        Tuple: (match percentage (float), list of matching skills)
    """
    if not required_skills:
        return 0, []
    # Normalize skills to lowercase for comparison
    extracted_set = set(s.lower() for s in extracted_skills)
    required_set = set(s.lower() for s in required_skills)
    matching = extracted_set.intersection(required_set)
    percentage = (len(matching) / len(required_set)) * 100
    return round(percentage, 2), list(matching)

#############################################
# 5. Streamlit User Interface
#############################################

st.title("Resume Parser")

# Sidebar: Job Role Matching Settings
st.sidebar.header("Job Role Matching")
selected_field = st.sidebar.selectbox("Select Field of Work", list(FIELD_SKILLS.keys()))
selected_skills = st.sidebar.multiselect("Select Required Skills", options=FIELD_SKILLS[selected_field])

# File uploader: Supports multiple resume files (PDF, DOCX, or TXT)
uploaded_files = st.file_uploader(
    "Upload your resume files (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Processing file: {uploaded_file.name}")
        extension = uploaded_file.name.split('.')[-1].lower()

        # Determine which text extraction function to use based on file extension
        if extension == "pdf":
            resume_text = read_pdf(uploaded_file)
        elif extension == "docx":
            resume_text = read_docx(uploaded_file)
        elif extension == "txt":
            resume_text = read_txt(uploaded_file)
        else:
            st.error("Unsupported file format.")
            continue

        # Extract candidate details from the resume text
        name = extract_name(resume_text)
        emails = extract_emails(resume_text)
        phones = extract_phone_numbers(resume_text)
        skills_extracted = extract_skills(resume_text)

        # Calculate match percentage between extracted skills and user-selected required skills
        match_percentage, matched_skills = calculate_match_percentage(skills_extracted, selected_skills)

        # Display the extracted information
        st.subheader("Extracted Information")
        st.write(f"**Name:** {name}")
        st.write(f"**Emails:** {', '.join(emails) if emails else 'Not found'}")
        st.write(f"**Phone Numbers:** {', '.join(phones) if phones else 'Not found'}")
        st.write(f"**Extracted Skills:** {', '.join(skills_extracted) if skills_extracted else 'Not found'}")

        # Display job role matching details
        st.subheader("Job Role Matching")
        if selected_skills:
            st.metric(label="Match Percentage", value=f"{match_percentage}%")
            st.write(
                "**Matching Skills:** "
                f"<span style='color:green;font-weight:bold;'>"
                f"{', '.join(matched_skills) if matched_skills else 'None'}"
                f"</span>",
                unsafe_allow_html=True
            )
        else:
            st.write("Select required skills from the sidebar to see match percentage.")
