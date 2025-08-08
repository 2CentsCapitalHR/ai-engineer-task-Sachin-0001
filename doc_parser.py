import re
from typing import Dict, List, Tuple, Optional
from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


class DocumentParser:
    """Parser for .docx legal documents with document type identification."""
    
    def __init__(self):
        # Document type keywords for classification
        self.document_types = {
            "Articles of Association": [
                "articles of association", "articles", "aoa", "company constitution",
                "share capital", "shareholders", "directors", "objects clause"
            ],
            "Memorandum of Association": [
                "memorandum of association", "memorandum", "moa", "mou",
                "company name", "registered office", "objects"
            ],
            "Board Resolution": [
                "board resolution", "directors resolution", "board meeting",
                "directors meeting", "resolution of directors"
            ],
            "Shareholder Resolution": [
                "shareholder resolution", "shareholders resolution", "general meeting",
                "extraordinary general meeting", "egm", "agm"
            ],
            "Incorporation Application": [
                "incorporation application", "application for incorporation",
                "company registration", "registration application"
            ],
            "UBO Declaration": [
                "ubo declaration", "ultimate beneficial owner", "beneficial owner",
                "ownership declaration", "shareholder declaration"
            ],
            "Register of Members and Directors": [
                "register of members", "register of directors", "members register",
                "directors register", "shareholder register"
            ],
            "Change of Registered Address": [
                "change of address", "registered address", "address change",
                "change of registered office"
            ],
            "Employment Contract": [
                "employment contract", "employment agreement", "service agreement",
                "terms of employment", "employee contract"
            ],
            "Licensing Application": [
                "licensing application", "license application", "regulatory filing",
                "compliance filing", "regulatory application"
            ],
            "Commercial Agreement": [
                "commercial agreement", "commercial contract", "business agreement",
                "service agreement", "supply agreement"
            ],
            "Compliance Policy": [
                "compliance policy", "risk policy", "compliance framework",
                "risk management", "compliance manual"
            ]
        }
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract all text from a .docx file."""
        try:
            doc = Document(file_path)
            text = []
            
            for element in doc.element.body:
                if isinstance(element, CT_P):
                    paragraph = Paragraph(element, doc)
                    text.append(paragraph.text)
                elif isinstance(element, CT_Tbl):
                    table = Table(element, doc)
                    for row in table.rows:
                        for cell in row.cells:
                            text.append(cell.text)
            
            return '\n'.join(text)
        except Exception as e:
            raise Exception(f"Error parsing document {file_path}: {str(e)}")
    
    def identify_document_type(self, text: str) -> Tuple[str, float]:
        """Identify the most likely document type based on content."""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, keywords in self.document_types.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            scores[doc_type] = score / len(keywords) if keywords else 0
        
        # Find the document type with highest score
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0], best_type[1]
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract document sections based on common legal document structure."""
        sections = {}
        
        # Common section patterns
        section_patterns = [
            r'(?:^|\n)([A-Z][A-Z\s]+(?:CLAUSE|SECTION|ARTICLE)?\s*\d*[.:]?)\s*\n',
            r'(?:^|\n)(\d+\.\s*[A-Z][^.\n]+)',
            r'(?:^|\n)([A-Z][A-Z\s]+(?:AND|OR|OF)\s+[A-Z\s]+)',
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                section_title = match.group(1).strip()
                # Get content until next section or end
                start_pos = match.end()
                next_match = re.search(pattern, text[start_pos:], re.MULTILINE)
                end_pos = start_pos + next_match.start() if next_match else len(text)
                section_content = text[start_pos:end_pos].strip()
                
                if section_content:
                    sections[section_title] = section_content
        
        return sections
    
    def parse_document(self, file_path: str) -> Dict:
        """Parse a document and return structured information."""
        text = self.extract_text_from_docx(file_path)
        doc_type, confidence = self.identify_document_type(text)
        sections = self.extract_sections(text)
        
        return {
            "file_path": file_path,
            "document_type": doc_type,
            "confidence": confidence,
            "text": text,
            "sections": sections,
            "word_count": len(text.split())
        }
    
    def get_required_documents_for_process(self, process: str) -> List[str]:
        """Get list of required documents for a specific legal process."""
        process_requirements = {
            "Company Incorporation": [
                "Articles of Association",
                "Memorandum of Association", 
                "Incorporation Application",
                "UBO Declaration",
                "Register of Members and Directors"
            ],
            "Company Licensing": [
                "Licensing Application",
                "Articles of Association",
                "Memorandum of Association",
                "UBO Declaration",
                "Compliance Policy"
            ],
            "Employment Setup": [
                "Employment Contract",
                "Board Resolution",
                "Compliance Policy"
            ],
            "Commercial Agreement": [
                "Commercial Agreement",
                "Board Resolution",
                "Shareholder Resolution"
            ]
        }
        
        return process_requirements.get(process, [])
    
    def detect_process_from_documents(self, document_types: List[str]) -> str:
        """Detect the legal process based on uploaded documents."""
        process_scores = {
            "Company Incorporation": 0,
            "Company Licensing": 0,
            "Employment Setup": 0,
            "Commercial Agreement": 0
        }
        
        # Score each process based on document presence
        for doc_type in document_types:
            if doc_type in ["Articles of Association", "Memorandum of Association", "Incorporation Application"]:
                process_scores["Company Incorporation"] += 1
            if doc_type in ["Licensing Application", "Compliance Policy"]:
                process_scores["Company Licensing"] += 1
            if doc_type in ["Employment Contract"]:
                process_scores["Employment Setup"] += 1
            if doc_type in ["Commercial Agreement"]:
                process_scores["Commercial Agreement"] += 1
        
        # Return the process with highest score
        return max(process_scores.items(), key=lambda x: x[1])[0]
