import re
from typing import List, Dict, Any, Tuple
from doc_parser import DocumentParser


class RedFlagChecker:
    """Detects red flags and compliance issues in legal documents."""
    
    def __init__(self):
        self.parser = DocumentParser()
        
        # Red flag patterns
        self.red_flags = {
            "jurisdiction_issues": [
                r"UAE\s+Federal\s+Courts?",
                r"UAE\s+Federal\s+Law",
                r"Federal\s+Courts?\s+of\s+UAE",
                r"UAE\s+Commercial\s+Courts?",
                r"governing\s+law.*UAE",
                r"jurisdiction.*UAE\s+Federal"
            ],
            "missing_clauses": [
                r"objects\s+clause",
                r"share\s+capital",
                r"directors?\s+appointment",
                r"shareholders?\s+rights",
                r"registered\s+office",
                r"company\s+name"
            ],
            "ambiguous_language": [
                r"may\s+or\s+may\s+not",
                r"subject\s+to\s+approval",
                r"as\s+deemed\s+appropriate",
                r"reasonable\s+discretion",
                r"best\s+efforts",
                r"commercially\s+reasonable"
            ],
            "missing_signatures": [
                r"signature\s+block",
                r"executed\s+by",
                r"signed\s+by",
                r"authorized\s+signatory",
                r"witness\s+signature"
            ],
            "incomplete_info": [
                r"TBD",
                r"to\s+be\s+determined",
                r"to\s+be\s+agreed",
                r"placeholder",
                r"\[.*\]",
                r"___+"
            ],
            "non_compliant_structures": [
                r"bearer\s+shares",
                r"nominee\s+director",
                r"trust\s+structure",
                r"offshore\s+company",
                r"tax\s+haven"
            ]
        }
        
        # ADGM-specific compliance requirements
        self.adgm_requirements = {
            "Articles of Association": [
                "ADGM jurisdiction",
                "company objects",
                "share capital structure",
                "director appointment",
                "shareholder rights",
                "registered office"
            ],
            "Memorandum of Association": [
                "company name",
                "registered office",
                "objects clause",
                "liability of members",
                "capital structure"
            ],
            "Board Resolution": [
                "meeting date",
                "directors present",
                "resolution text",
                "voting results",
                "signature blocks"
            ],
            "UBO Declaration": [
                "beneficial owner details",
                "ownership percentages",
                "control structures",
                "declaration statements",
                "supporting documentation"
            ]
        }
    
    def check_jurisdiction_issues(self, text: str) -> List[Dict[str, Any]]:
        """Check for jurisdiction-related red flags."""
        issues = []
        text_lower = text.lower()
        
        for pattern in self.red_flags["jurisdiction_issues"]:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "jurisdiction_issue",
                    "severity": "High",
                    "description": f"Reference to UAE Federal Courts instead of ADGM",
                    "location": f"Position {match.start()}-{match.end()}",
                    "suggestion": "Replace with ADGM jurisdiction references",
                    "adgm_reference": "ADGM Companies Regulations 2020, Article 6"
                })
        
        return issues
    
    def check_missing_clauses(self, text: str, document_type: str) -> List[Dict[str, Any]]:
        """Check for missing essential clauses."""
        issues = []
        text_lower = text.lower()
        
        # Check for document-specific requirements
        if document_type in self.adgm_requirements:
            required_clauses = self.adgm_requirements[document_type]
            for clause in required_clauses:
                if clause.lower() not in text_lower:
                    issues.append({
                        "type": "missing_clause",
                        "severity": "High",
                        "description": f"Missing required clause: {clause}",
                        "suggestion": f"Add {clause} section to comply with ADGM requirements",
                        "adgm_reference": f"ADGM Companies Regulations 2020"
                    })
        
        return issues
    
    def check_ambiguous_language(self, text: str) -> List[Dict[str, Any]]:
        """Check for ambiguous or non-binding language."""
        issues = []
        text_lower = text.lower()
        
        for pattern in self.red_flags["ambiguous_language"]:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "ambiguous_language",
                    "severity": "Medium",
                    "description": f"Ambiguous language found: '{match.group()}'",
                    "location": f"Position {match.start()}-{match.end()}",
                    "suggestion": "Replace with specific, binding language",
                    "adgm_reference": "ADGM Companies Regulations 2020"
                })
        
        return issues
    
    def check_missing_signatures(self, text: str) -> List[Dict[str, Any]]:
        """Check for missing signature sections."""
        issues = []
        text_lower = text.lower()
        
        signature_found = False
        for pattern in self.red_flags["missing_signatures"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                signature_found = True
                break
        
        if not signature_found:
            issues.append({
                "type": "missing_signatures",
                "severity": "High",
                "description": "Missing signature section",
                "suggestion": "Add proper signature blocks with witness signatures",
                "adgm_reference": "ADGM Companies Regulations 2020"
            })
        
        return issues
    
    def check_incomplete_info(self, text: str) -> List[Dict[str, Any]]:
        """Check for incomplete or placeholder information."""
        issues = []
        
        for pattern in self.red_flags["incomplete_info"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "incomplete_info",
                    "severity": "Medium",
                    "description": f"Incomplete information: '{match.group()}'",
                    "location": f"Position {match.start()}-{match.end()}",
                    "suggestion": "Complete all required information before submission",
                    "adgm_reference": "ADGM Companies Regulations 2020"
                })
        
        return issues
    
    def check_non_compliant_structures(self, text: str) -> List[Dict[str, Any]]:
        """Check for non-compliant corporate structures."""
        issues = []
        text_lower = text.lower()
        
        for pattern in self.red_flags["non_compliant_structures"]:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "non_compliant_structure",
                    "severity": "High",
                    "description": f"Non-compliant structure: '{match.group()}'",
                    "location": f"Position {match.start()}-{match.end()}",
                    "suggestion": "Review structure for ADGM compliance",
                    "adgm_reference": "ADGM Companies Regulations 2020"
                })
        
        return issues
    
    def check_formatting_issues(self, text: str) -> List[Dict[str, Any]]:
        """Check for formatting and structural issues."""
        issues = []
        
        # Check for proper paragraph structure
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 3:
            issues.append({
                "type": "formatting_issue",
                "severity": "Low",
                "description": "Document appears to have insufficient structure",
                "suggestion": "Organize document into clear sections with proper headings",
                "adgm_reference": "ADGM Document Standards"
            })
        
        # Check for proper numbering
        if not re.search(r'\d+\.', text):
            issues.append({
                "type": "formatting_issue",
                "severity": "Low",
                "description": "Document lacks proper clause numbering",
                "suggestion": "Add numbered clauses for better organization",
                "adgm_reference": "ADGM Document Standards"
            })
        
        return issues
    
    def analyze_document(self, text: str, document_type: str) -> Dict[str, Any]:
        """Comprehensive document analysis for red flags."""
        all_issues = []
        
        # Run all checks
        all_issues.extend(self.check_jurisdiction_issues(text))
        all_issues.extend(self.check_missing_clauses(text, document_type))
        all_issues.extend(self.check_ambiguous_language(text))
        all_issues.extend(self.check_missing_signatures(text))
        all_issues.extend(self.check_incomplete_info(text))
        all_issues.extend(self.check_non_compliant_structures(text))
        all_issues.extend(self.check_formatting_issues(text))
        
        # Calculate overall severity
        severity_scores = {"Low": 1, "Medium": 2, "High": 3}
        max_severity = max([severity_scores.get(issue["severity"], 1) for issue in all_issues]) if all_issues else 0
        
        overall_severity = "Low"
        if max_severity >= 3:
            overall_severity = "High"
        elif max_severity >= 2:
            overall_severity = "Medium"
        
        # Group issues by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        return {
            "document_type": document_type,
            "total_issues": len(all_issues),
            "overall_severity": overall_severity,
            "issues": all_issues,
            "issues_by_type": issues_by_type,
            "summary": {
                "jurisdiction_issues": len([i for i in all_issues if i["type"] == "jurisdiction_issue"]),
                "missing_clauses": len([i for i in all_issues if i["type"] == "missing_clause"]),
                "ambiguous_language": len([i for i in all_issues if i["type"] == "ambiguous_language"]),
                "missing_signatures": len([i for i in all_issues if i["type"] == "missing_signatures"]),
                "incomplete_info": len([i for i in all_issues if i["type"] == "incomplete_info"]),
                "non_compliant_structures": len([i for i in all_issues if i["type"] == "non_compliant_structure"]),
                "formatting_issues": len([i for i in all_issues if i["type"] == "formatting_issue"])
            }
        }
    
    def generate_compliance_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable compliance report."""
        report = f"""
# ADGM Compliance Analysis Report

**Document Type:** {analysis['document_type']}
**Overall Severity:** {analysis['overall_severity']}
**Total Issues Found:** {analysis['total_issues']}

## Summary
"""
        
        for issue_type, count in analysis['summary'].items():
            if count > 0:
                report += f"- {issue_type.replace('_', ' ').title()}: {count}\n"
        
        report += "\n## Detailed Issues\n"
        
        for issue in analysis['issues']:
            report += f"""
### {issue['type'].replace('_', ' ').title()}
- **Severity:** {issue['severity']}
- **Description:** {issue['description']}
- **Suggestion:** {issue['suggestion']}
- **ADGM Reference:** {issue.get('adgm_reference', 'N/A')}
"""
        
        return report
