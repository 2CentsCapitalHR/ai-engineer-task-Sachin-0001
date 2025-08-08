import streamlit as st
import os
import json
import tempfile
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

# Import our custom modules
from doc_parser import DocumentParser
from rag_engine import RAGEngine
from redfalg_checker import RedFlagChecker
from comment_inserter import CommentInserter


class CorporateAgent:
    """Main Corporate Agent class that orchestrates the entire system."""
    
    def __init__(self):
        self.parser = DocumentParser()
        self.rag_engine = RAGEngine()
        self.red_flag_checker = RedFlagChecker()
        self.comment_inserter = CommentInserter()
        
        # Create outputs directory if it doesn't exist
        os.makedirs("outputs", exist_ok=True)
    
    def process_documents(self, uploaded_files: List) -> Dict[str, Any]:
        """Process uploaded documents and return comprehensive analysis."""
        results = {
            "documents_analyzed": [],
            "process_detected": "",
            "missing_documents": [],
            "overall_analysis": {},
            "reviewed_files": []
        }
        
        # Parse each uploaded document
        for uploaded_file in uploaded_files:
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Parse document
                doc_info = self.parser.parse_document(tmp_path)
                
                # Analyze for red flags
                red_flag_analysis = self.red_flag_checker.analyze_document(
                    doc_info["text"], 
                    doc_info["document_type"]
                )
                
                # Get RAG-based compliance analysis
                rag_analysis = self.rag_engine.analyze_document_compliance(
                    doc_info["text"], 
                    doc_info["document_type"]
                )
                
                # Create reviewed document with comments
                reviewed_path = self._create_reviewed_document(
                    tmp_path, 
                    red_flag_analysis["issues"], 
                    doc_info["document_type"]
                )
                
                # Store results
                document_result = {
                    "file_name": uploaded_file.name,
                    "document_type": doc_info["document_type"],
                    "confidence": doc_info["confidence"],
                    "word_count": doc_info["word_count"],
                    "red_flag_analysis": red_flag_analysis,
                    "rag_analysis": rag_analysis,
                    "reviewed_file_path": reviewed_path
                }
                
                results["documents_analyzed"].append(document_result)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Detect process and check missing documents
        if results["documents_analyzed"]:
            document_types = [doc["document_type"] for doc in results["documents_analyzed"]]
            detected_process = self.parser.detect_process_from_documents(document_types)
            results["process_detected"] = detected_process
            
            # Check for missing documents
            required_docs = self.parser.get_required_documents_for_process(detected_process)
            uploaded_doc_types = set(document_types)
            missing_docs = [doc for doc in required_docs if doc not in uploaded_doc_types]
            results["missing_documents"] = missing_docs
            
            # Add missing keys that the UI expects
            results["documents_uploaded"] = len(results["documents_analyzed"])
            results["required_documents"] = len(required_docs)
        
        return results
    
    def _create_reviewed_document(self, original_path: str, issues: List[Dict], 
                                document_type: str) -> str:
        """Create a reviewed version of the document."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"reviewed_{document_type.replace(' ', '_')}_{timestamp}.docx"
        output_path = os.path.join("outputs", output_filename)
        
        try:
            # Create reviewed document with comments
            reviewed_path = self.comment_inserter.create_reviewed_document(
                original_path, issues, output_path
            )
            return reviewed_path
        except Exception as e:
            st.error(f"Error creating reviewed document: {str(e)}")
            return None
    
    def generate_structured_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured JSON report as specified in requirements."""
        report = {
            "process": results.get("process_detected", "Unknown"),
            "documents_uploaded": len(results.get("documents_analyzed", [])),
            "required_documents": 0,
            "missing_document": "",
            "issues_found": []
        }
        
        # Calculate required documents
        if results.get("process_detected"):
            required_docs = self.parser.get_required_documents_for_process(
                results["process_detected"]
            )
            report["required_documents"] = len(required_docs)
            
            # Set missing document
            missing_docs = results.get("missing_documents", [])
            if missing_docs:
                report["missing_document"] = missing_docs[0]
        
        # Collect all issues
        for doc_result in results.get("documents_analyzed", []):
            doc_name = doc_result["file_name"]
            doc_type = doc_result["document_type"]
            
            # Add red flag issues
            for issue in doc_result["red_flag_analysis"].get("issues", []):
                report["issues_found"].append({
                    "document": doc_type,
                    "section": issue.get("location", "General"),
                    "issue": issue.get("description", ""),
                    "severity": issue.get("severity", "Medium"),
                    "suggestion": issue.get("suggestion", "")
                })
        
        return report


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="ADGM Corporate Agent",
        page_icon="🏢",
        layout="wide"
    )
    
    st.title("🏢 ADGM Corporate Agent")
    st.subheader("AI-Powered Legal Document Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # About section
        st.header("About")
        st.markdown("""
        This Corporate Agent helps you:
        - 📄 Review legal documents for ADGM compliance
        - 🚨 Detect red flags and issues
        - ✅ Verify document completeness
        - 💬 Add contextual comments
        - 📋 Generate compliance reports
        """)
        
        st.info("🤖 Powered by Groq API")
    
    # Main content area
    uploaded_files = None
    try:
        # Initialize Corporate Agent
        agent = CorporateAgent()
        
        # File upload section
        st.header("📄 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload your .docx legal documents",
            type=["docx"],
            accept_multiple_files=True,
            help="Upload one or more .docx files for analysis"
        )
        
        if uploaded_files:
            st.success(f"✅ Uploaded {len(uploaded_files)} document(s)")
            
            # Process documents
            with st.spinner("🤖 Analyzing documents..."):
                results = agent.process_documents(uploaded_files)
            
            # Display results
            if results["documents_analyzed"]:
                st.header("📊 Analysis Results")
                
                # Process detection
                if results["process_detected"]:
                    st.subheader(f"🎯 Detected Process: {results['process_detected']}")
                    
                    # Document checklist
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Documents Uploaded", 
                            results["documents_uploaded"]
                        )
                    with col2:
                        st.metric(
                            "Required Documents", 
                            results["required_documents"]
                        )
                    
                    # Missing documents alert
                    if results["missing_documents"]:
                        st.warning(f"""
                        ⚠️ **Missing Documents Detected**
                        
                        It appears that you're trying to {results['process_detected'].lower()} in ADGM. 
                        Based on our reference list, you have uploaded {results['documents_uploaded']} out of {results['required_documents']} required documents.
                        
                        **Missing document(s):** {', '.join(results['missing_documents'])}
                        """)
                
                # Document analysis results
                st.subheader("📋 Document Analysis")
                
                for doc_result in results["documents_analyzed"]:
                    with st.expander(f"📄 {doc_result['file_name']} ({doc_result['document_type']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Confidence", f"{doc_result['confidence']:.1%}")
                        with col2:
                            st.metric("Word Count", doc_result['word_count'])
                        with col3:
                            st.metric("Issues Found", doc_result['red_flag_analysis']['total_issues'])
                        
                        # Issues summary
                        if doc_result['red_flag_analysis']['issues']:
                            st.write("**Issues Found:**")
                            for issue in doc_result['red_flag_analysis']['issues'][:5]:  # Show first 5
                                severity_color = {
                                    "High": "🔴",
                                    "Medium": "🟡", 
                                    "Low": "🟢"
                                }.get(issue['severity'], "⚪")
                                
                                st.write(f"{severity_color} **{issue['severity']}**: {issue['description']}")
                        
                        # Download reviewed document
                        if doc_result['reviewed_file_path']:
                            with open(doc_result['reviewed_file_path'], 'rb') as f:
                                st.download_button(
                                    label=f"📥 Download Reviewed {doc_result['document_type']}",
                                    data=f.read(),
                                    file_name=f"reviewed_{doc_result['file_name']}",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                
                # Generate structured report
                st.subheader("📊 Structured Report")
                structured_report = agent.generate_structured_report(results)
                
                # Display report
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json(structured_report)
                
                with col2:
                    # Download JSON report
                    json_str = json.dumps(structured_report, indent=2)
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json_str,
                        file_name="adgm_analysis_report.json",
                        mime="application/json"
                    )
                    
                    # Download CSV report
                    if structured_report["issues_found"]:
                        df = pd.DataFrame(structured_report["issues_found"])
                        csv_str = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV Report",
                            data=csv_str,
                            file_name="adgm_issues_report.csv",
                            mime="text/csv"
                        )
            
            else:
                st.error("❌ No documents were successfully processed.")
    
    except Exception as e:
        st.error(f"❌ Error initializing Corporate Agent: {str(e)}")
        if "GROQ_API_KEY" in str(e):
            st.info("""
            **To fix this issue:**
            
            1. Get your Groq API key from: https://console.groq.com/
            2. Set the environment variable:
            
            **Windows (PowerShell):**
            ```powershell
            $env:GROQ_API_KEY="your_api_key_here"
            ```
            
            **Windows (CMD):**
            ```cmd
            set GROQ_API_KEY=your_api_key_here
            ```
            
            **macOS/Linux:**
            ```bash
            export GROQ_API_KEY=your_api_key_here
            ```
            
            3. Restart the application
            """)
        else:
            st.info("Please try again or check your internet connection.")
    
    # Show features when no documents are uploaded
    if not uploaded_files:
        st.header("🎯 Features")
        st.markdown("""
        ### Document Processing
        - **Multi-document upload**: Upload multiple .docx files simultaneously
        - **Automatic classification**: Identify document types (AoA, MoA, etc.)
        - **Process detection**: Determine legal process (incorporation, licensing, etc.)
        
        ### Compliance Analysis
        - **Red flag detection**: Identify jurisdiction issues, missing clauses, etc.
        - **ADGM compliance**: Check against ADGM regulations and requirements
        - **Missing document alerts**: Notify about required documents
        
        ### Document Enhancement
        - **Contextual comments**: Add legal references and suggestions
        - **Highlighted sections**: Mark problematic areas
        - **Downloadable output**: Get reviewed documents with comments
        
        ### Reporting
        - **Structured JSON**: Machine-readable analysis results
        - **CSV export**: Detailed issues breakdown
        - **Compliance summaries**: Human-readable reports
        """)
        
        st.header("📋 Supported Document Types")
        st.markdown("""
        - **Company Formation**: Articles of Association, Memorandum of Association
        - **Regulatory**: UBO Declarations, Incorporation Applications
        - **Corporate**: Board Resolutions, Shareholder Resolutions
        - **Employment**: Employment Contracts, HR Policies
        - **Commercial**: Commercial Agreements, Licensing Applications
        """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏢 ADGM Corporate Agent | AI-Powered Legal Assistant</p>
        <p>Built for Abu Dhabi Global Market (ADGM) compliance</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
