import streamlit as st
import re
import spacy
import pdfplumber  # Library for reading PDF files
from docx import Document  # Library for reading DOCX files

#############################################
# 1. Define Skills Database and Field Mapping
#############################################

# List of skills (technical & non-technical) to look for in resumes
SKILLS_DB = [
    # Technical Skills
    "python", "java", "c++", "sql", "machine learning", "data analysis",
    "tensorflow", "pytorch", "scikit-learn", "nlp", "deep learning",
    "html", "css", "javascript", "react", "angular", "node.js", "django", "flask",
    "aws", "azure", "gcp", "docker", "kubernetes", "cybersecurity", "data visualization",
    "software development", "api development", "cloud computing", "blockchain", "microservices",
    "big data", "hadoop", "spark", "tableau", "power bi", "data mining", "ai ethics",
    "robotics", "embedded systems", "computer vision", "image processing",
    "ethical hacking", "penetration testing", "iot", "devops", "graphql", "rest api",
    "web development", "mobile development", "android", "ios", "swift", "kotlin",
    "game development", "unity", "unreal engine", "c#", "3d modeling", "animation",
    "quantum computing", "network security", "cryptography", "bioinformatics",
    "matlab", "r programming", "sas", "statistical analysis", "genetic algorithms",
    "autocad", "solidworks", "finite element analysis", "control systems",

    # Non-Technical / Soft Skills
    "communication", "project management", "leadership", "teamwork", "problem solving",
    "time management", "critical thinking", "creativity", "adaptability", "conflict resolution",
    "customer service", "sales", "marketing", "strategic planning", "negotiation",
    "budget management", "public speaking", "event planning", "human resources", "finance",
    "accounting", "research", "writing", "organization", "interpersonal skills",
    "presentation skills", "active listening", "decision making", "emotional intelligence",
    "mentoring", "coaching", "networking", "cross-functional collaboration",
    "stakeholder management", "change management", "stress management", "cultural awareness",
    "diversity and inclusion", "team building", "self-motivation", "resilience",
    "work ethic", "multitasking", "conflict mediation", "persuasion",
    "analytical thinking", "design thinking", "customer relationship management (crm)"
]


# Mapping between job fields and required skills
FIELD_SKILLS = {
    "Computer Science": [
        "python", "java", "c++", "sql", "machine learning", "data analysis",
        "tensorflow", "pytorch", "scikit-learn", "nlp", "deep learning",
        "software development", "api development", "cloud computing",
        "cybersecurity", "blockchain", "devops", "big data", "artificial intelligence"
    ],
    "Teaching": [
        "communication", "leadership", "teamwork", "time management",
        "critical thinking", "creativity", "curriculum development", "public speaking",
        "educational technology", "student assessment"
    ],
    "Marketing": [
        "communication", "strategic planning", "negotiation", "sales",
        "marketing", "digital marketing", "seo", "content creation", "social media",
        "branding", "advertising", "market research", "email marketing"
    ],
    "Finance": [
        "accounting", "budget management", "financial analysis", "data analysis",
        "excel", "risk management", "finance", "investment management", "cryptocurrency",
        "financial modeling"
    ],
    "Healthcare": [
        "patient care", "medical terminology", "communication", "empathy",
        "teamwork", "data analysis", "organization", "health informatics",
        "clinical research", "telemedicine"
    ],
    "Engineering": [
        "mechanical engineering", "electrical engineering", "civil engineering",
        "structural analysis", "matlab", "cad", "robotics", "control systems"
    ],
    "Human Resources": [
        "recruitment", "employee relations", "performance management",
        "hr policies", "conflict resolution", "talent acquisition"
    ],
    "Law": [
        "legal research", "contract law", "intellectual property law",
        "corporate law", "litigation", "compliance"
    ],
    "E-commerce": [
        "shopify", "woocommerce", "customer experience", "e-commerce marketing",
        "conversion rate optimization", "inventory management"
    ],
    "Graphic Design": [
        "photoshop", "illustrator", "figma", "ui/ux design", "typography",
        "branding", "motion graphics"
    ],
    "Project Management": [
        "agile", "scrum", "kanban", "risk management", "budgeting",
        "stakeholder communication"
    ],
    "Data Science": [
        "data visualization", "data engineering", "sql", "python",
        "r programming", "machine learning", "deep learning"
    ],
    "Game Development": [
        "unity", "unreal engine", "c#", "game physics", "3d modeling",
        "game design", "shader programming"
    ],
    "Cybersecurity": [
        "penetration testing", "network security", "encryption", "ethical hacking",
        "incident response", "firewall management"
    ],
    "Robotics": [
        "robot kinematics", "ros", "automation", "control systems",
        "embedded systems", "sensor fusion"
    ],
    "Biotechnology": [
        "genetic engineering", "bioprocessing", "molecular biology",
        "bioinformatics", "clinical research"
    ],
    "Environmental Science": [
        "climate change", "sustainability", "waste management", "ecology",
        "environmental impact assessment"
    ],
    "Sports Science": [
        "exercise physiology", "sports nutrition", "biomechanics",
        "athletic training", "injury prevention"
    ],
    "Hospitality Management": [
        "hotel management", "event planning", "customer service",
        "food and beverage management", "tourism"
    ],
    "Aerospace Engineering": [
        "aerodynamics", "propulsion systems", "avionics",
        "aircraft design", "flight simulation"
    ],
    "Fashion Design": [
        "textile design", "pattern making", "fashion illustration",
        "trend analysis", "garment construction"
    ]
}

#############################################
# 2. Load and Cache spaCy Model
#############################################

@st.cache_resource
def load_nlp_model():
    """
    Load the spaCy language model and cache it for session reuse.
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
    """Extract text from a PDF file using pdfplumber."""
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
    """Extract text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
    return text

def read_txt(file):
    """Extract text from a TXT file."""
    text = ""
    try:
        text = file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
    return text

#############################################
# 4. Extraction Functions
#############################################
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
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name_pattern = r"^(Dr\.|Mr\.|Ms\.|Mrs\.)?\s*[A-Za-z\s,]+(,\s*(MD|PhD|Jr\.|Sr\.))?$"
    excluded_headers = {"work experience", "education history", "relevant skills", 
                       "volunteer work", "geriatric medicine", "contact information"}
    for i, line in enumerate(lines[:5]):
        if (re.match(name_pattern, line) and 
            line.lower() not in excluded_headers):
            return line
        else:
            return "Not found"
        
def extract_emails(text):
    """Extract all email addresses from text using regex."""
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(email_pattern, text)

def extract_phone_numbers(text):
    """Extract phone numbers from text using regex."""
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    return re.findall(phone_pattern, text)

def extract_skills(text):
    """Extract skills from text by matching with predefined skill list."""
    text_lower = text.lower()
    found_skills = [skill for skill in SKILLS_DB if skill.lower() in text_lower]
    return list(set(found_skills))  # Remove duplicates

def calculate_match_percentage(extracted_skills, required_skills):
    """Calculate skill match percentage between extracted and required skills."""
    if not required_skills:
        return 0, []
    extracted_set = set(map(str.lower, extracted_skills))
    required_set = set(map(str.lower, required_skills))
    matching = extracted_set.intersection(required_set)
    percentage = (len(matching) / len(required_set)) * 100
    return round(percentage, 2), list(matching)

#############################################
# 5. Streamlit User Interface
#############################################

st.title("Resume Parser")

# Sidebar: Job Role Matching
st.sidebar.header("Job Role Matching")
selected_field = st.sidebar.selectbox("Select Field of Work", list(FIELD_SKILLS.keys()))
selected_skills = st.sidebar.multiselect("Select Required Skills", options=FIELD_SKILLS[selected_field])

# File uploader: Accepts multiple resume files
uploaded_files = st.file_uploader("Upload resumes (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Processing file: {uploaded_file.name}")
        extension = uploaded_file.name.split('.')[-1].lower()

        # Read the file based on its format
        resume_text = read_pdf(uploaded_file) if extension == "pdf" else read_docx(uploaded_file) if extension == "docx" else read_txt(uploaded_file)

        # Extract details
        name = extract_name(resume_text)
        emails = extract_emails(resume_text)
        phones = extract_phone_numbers(resume_text)
        skills_extracted = extract_skills(resume_text)
        match_percentage, matched_skills = calculate_match_percentage(skills_extracted, selected_skills)

        # Display extracted details
        st.subheader("Extracted Information")
        st.write(f"**Name:** {''.join(name) if name else 'Not found'}")
        st.write(f"**Emails:** {', '.join(emails) if emails else 'Not found'}")
        st.write(f"**Phone Numbers:** {', '.join(phones) if phones else 'Not found'}")
        st.write(f"**Extracted Skills:** {', '.join(skills_extracted) if skills_extracted else 'Not found'}")
        
        st.subheader("Job Role Matching")
        if selected_skills:
            st.metric(label="Match Percentage", value=f"{match_percentage}%")
