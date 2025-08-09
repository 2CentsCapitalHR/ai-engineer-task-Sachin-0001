# 🧠 ADGM Corporate Agent – AI Legal Assistant

This project is a take-home assignment for the **AI Engineer Intern position at 2Cents Capital**. It implements an intelligent AI-powered legal assistant, the **Corporate Agent**, that assists with document validation, compliance checking, and feedback generation for companies looking to incorporate within the **Abu Dhabi Global Market (ADGM)** jurisdiction.

---

## 🚀 Features

- 📄 Accepts `.docx` legal documents
- 🧠 Uses **RAG (Retrieval-Augmented Generation)** to refer to ADGM rules
- ✅ Detects missing or non-compliant documents based on legal checklists
- 🚨 Flags red flags such as:
  - Invalid or missing clauses
  - Wrong jurisdiction (UAE Federal Courts vs ADGM)
  - Ambiguous/non-binding language
  - Missing signature sections
- 💬 Inserts contextual comments with legal references (e.g., ADGM Companies Regulations 2020, Art. 6)
- 📥 Outputs:
  - Reviewed `.docx` file with comments
  - Structured `JSON` or `Python` dictionary summary inside outputs folder

---

## 🗂 Document Categories Handled

### 📌 Company Formation Documents:
- Articles of Association (AoA)
- Memorandum of Association (MoA)
- UBO Declaration Form
- Incorporation Application Form
- Board/Shareholder Resolutions
- Register of Members and Directors
- Change of Address Notice

### 📁 Other Categories:
- Employment Contracts
- Licensing & Regulatory Filings
- Risk & Compliance Policies

---

## 💻 Tech Stack

| Component        | Tools Used                          |
|------------------|-------------------------------------|
| UI               | Streamlit                          |
| NLP & RAG        | Groq API + FAISS + LangChain        |
| Document Parsing | `python-docx`, `docx`               |
| Comments         | `python-docx`                       |
| Data Sources     | Official ADGM PDF & Word templates  |

---

## 🛠️ Setup Instructions

### 1. **Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Set Up Environment**
Set your Groq API key as an environment variable. End users are not prompted for any keys.
```bash
# On Windows (PowerShell)
$env:GROQ_API_KEY="your_groq_api_key_here"

# On Windows (cmd)
set GROQ_API_KEY=your_groq_api_key_here

# On macOS/Linux
export GROQ_API_KEY=your_groq_api_key_here
```

No OpenAI key is required. Embeddings use a local Hugging Face model.

### 4. **Run the Application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📥 Inputs

Upload one or more `.docx` files via the UI(present in examples folder).

---

## 📤 Outputs

- 📄 A downloadable `.docx` file with inline comments inserted at relevant sections.
- 🧾 A structured `JSON` or Python dictionary summarizing the analysis:
  - Detected process (e.g., "Company Incorporation")
  - Number of uploaded vs. required documents
  - Missing documents
  - Issues found, severity, and suggestions

---

## 🔧 Example Output

```json
{
  "process": "Company Incorporation",
  "documents_uploaded": 4,
  "required_documents": 5,
  "missing_document": "Register of Members and Directors",
  "issues_found": [
    {
      "document": "Articles of Association",
      "section": "Clause 3.1",
      "issue": "Jurisdiction clause does not specify ADGM",
      "severity": "High",
      "suggestion": "Update jurisdiction to ADGM Courts."
    }
  ]
}
```

---

## 🏗️ Project Structure

```
ai-engineer-task-Sachin-0001/
├── app.py                      # Main Streamlit application
├── doc_parser.py              # Document parsing and classification
├── rag_engine.py              # RAG engine for legal knowledge
├── redfalg_checker.py         # Red flag detection
├── comment_inserter.py        # Comment insertion in documents
├── create_sample_documents.py # Sample document generator
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── data/                     # ADGM reference materials
├── examples/                 # Sample documents
└── outputs/                  # Generated reviewed documents
```

---

## 🧪 Testing

### Sample Documents
The system includes sample documents with known issues:

1. **Articles of Association** - Contains jurisdiction issues and incomplete signatures
2. **Memorandum of Association** - Basic compliant document
3. **UBO Declaration** - Contains placeholder information
4. **Board Resolution** - Missing specific details

### Expected Red Flags
- References to "UAE Federal Courts" instead of ADGM
- Incomplete signature sections
- Placeholder text like "[TBD]"
- Ambiguous language like "as deemed appropriate"

---

## 🔍 Key Features Explained

### 1. **Document Classification**
- Uses keyword matching to identify document types
- Supports 12+ document categories
- Provides confidence scores for classification

### 2. **Red Flag Detection**
- **Jurisdiction Issues**: Detects references to UAE Federal Courts
- **Missing Clauses**: Checks for required ADGM-specific sections
- **Ambiguous Language**: Identifies non-binding or vague terms
- **Incomplete Information**: Finds placeholders and missing data
- **Signature Issues**: Validates proper signature blocks

### 3. **RAG Integration**
- Built-in ADGM legal knowledge base
- References specific regulations (Companies Regulations 2020)
- Provides contextual suggestions with legal citations

### 4. **Process Detection**
- Automatically identifies legal processes (incorporation, licensing, etc.)
- Compares uploaded documents against required checklists
- Alerts about missing mandatory documents

---

## 🚨 Common Issues Detected

| Issue Type | Description | Severity |
|------------|-------------|----------|
| Jurisdiction | References to UAE Federal Courts | High |
| Missing Clauses | Required ADGM sections missing | High |
| Ambiguous Language | Non-binding or vague terms | Medium |
| Incomplete Info | Placeholders like [TBD] | Medium |
| Missing Signatures | Incomplete signature blocks | High |

---

## 📋 Compliance Checklist

### Company Incorporation Requirements:
- ✅ Articles of Association
- ✅ Memorandum of Association
- ✅ Incorporation Application
- ✅ UBO Declaration
- ✅ Register of Members and Directors

### Company Licensing Requirements:
- ✅ Licensing Application
- ✅ Articles of Association
- ✅ Memorandum of Association
- ✅ UBO Declaration
- ✅ Compliance Policy

---

## 🔧 Troubleshooting

### Common Issues:

1. **Groq API Key**
   - Set `GROQ_API_KEY` in your environment
   - Ensure the key is valid

2. **Document Processing Error**
   - Ensure uploaded files are valid `.docx` format
   - Check file size (should be under 10MB)

3. **Module Import Errors**
   - Run `pip install -r requirements.txt` again
   - Check Python version (3.8+ required)

---