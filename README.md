# Resume Parser with Job Role Matching

**Short Description (under 350 characters):**  
This Streamlit app parses resumes (PDF, DOCX, or TXT) using spaCy and pdfplumber. It extracts name, email, phone, and skills, then compares them to field-specific requirements for a match percentage. Great for quickly evaluating how well a resume matches a given job role.

## Environment Setup

It's recommended to use a virtual environment to isolate dependencies:

```bash
python -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate     # On Windows
```
## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Where `requirements.txt` might look like this:

```ruby
streamlit
spacy
pdfplumber
python-docx
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.5.0/en_core_web_sm-3.5.0.tar.gz
```
After installing, download the spaCy model:

```bash
python -m spacy download en_core_web_sm
```

## Usage

1. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
2. **Upload Resumes**: In the web UI, upload PDF, DOCX, or TXT resume files.
3. **Select Field & Skills**: Use the sidebar to choose a field (e.g., Computer Science) and pick relevant skills.
4. **View Results**: The app displays extracted name, emails, phone, skills, and a match percentage for the chosen role.

### Customization
- **Update `SKILLS_DB`** for additional or domain-specific skills.
- **Adjust `FIELD_SKILLS`** for new fields or to remove existing ones.
- **Modify `extract_name`, `extract_phone_numbers`, or other extraction functions** in `app.py` to refine parsing logic.
