import os
import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.schema import Document


class RAGEngine:
    """RAG engine for ADGM legal knowledge and document analysis."""
    
    def __init__(self):
        # Use Groq API via environment variable; users are not prompted in UI
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required. "
                "Please set it using:\n"
                "Windows (PowerShell): $env:GROQ_API_KEY='your_api_key_here'\n"
                "Windows (CMD): set GROQ_API_KEY=your_api_key_here\n"
                "macOS/Linux: export GROQ_API_KEY=your_api_key_here\n\n"
                "Get your API key from: https://console.groq.com/"
            )
        
        # Initialize TF-IDF vectorizer for simple text similarity
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Initialize LLM with Groq
        self.llm = ChatGroq(
            model_name="llama3-8b-8192",
            temperature=0.1,
            groq_api_key=self.groq_api_key
        )
        
        # ADGM legal knowledge base
        self.adgm_knowledge = self._load_adgm_knowledge()
        self.vector_store = None
        self._initialize_vector_store()
    
    def _load_adgm_knowledge(self) -> List[Document]:
        """Load ADGM legal knowledge and regulations."""
        knowledge_base = [
            # ADGM Companies Regulations 2020
            Document(
                page_content="""
                ADGM Companies Regulations 2020 - Key Provisions:
                
                Article 6: Company Formation
                - Companies must be incorporated under ADGM regulations
                - Articles of Association must specify ADGM jurisdiction
                - Memorandum of Association must include company objects
                
                Article 12: Share Capital
                - Minimum share capital requirements
                - Share capital must be specified in Articles
                - Shares must be fully paid up
                
                Article 15: Directors
                - Minimum one director required
                - Directors must be natural persons
                - Register of directors must be maintained
                
                Article 18: Shareholders
                - Register of members must be maintained
                - UBO declarations required
                - Shareholder rights and obligations
                
                Article 25: Registered Office
                - Must have registered office in ADGM
                - Address change notifications required
                - Physical presence requirements
                """,
                metadata={"source": "ADGM Companies Regulations 2020", "type": "regulation"}
            ),
            
            # ADGM Licensing Requirements
            Document(
                page_content="""
                ADGM Licensing Requirements:
                
                Financial Services Permission (FSP):
                - Application form with detailed business plan
                - Fit and proper person assessments
                - Capital adequacy requirements
                - Compliance framework documentation
                
                Commercial License:
                - Business activity description
                - Shareholder and director details
                - Financial projections
                - Compliance policies
                
                Employment Regulations:
                - Standard employment contracts
                - Work permit requirements
                - Labor law compliance
                - Employee benefits structure
                """,
                metadata={"source": "ADGM Licensing Guide", "type": "licensing"}
            ),
            
            # Common Legal Issues
            Document(
                page_content="""
                Common Legal Issues in ADGM Documents:
                
                Jurisdiction Issues:
                - References to UAE Federal Courts instead of ADGM
                - Incorrect governing law clauses
                - Missing ADGM-specific provisions
                
                Compliance Issues:
                - Missing UBO declarations
                - Incomplete director information
                - Insufficient share capital details
                - Missing compliance policies
                
                Structural Issues:
                - Ambiguous language in clauses
                - Missing essential sections
                - Incorrect formatting
                - Non-binding provisions
                
                Red Flags:
                - References to other jurisdictions
                - Missing signature blocks
                - Incomplete corporate information
                - Non-compliant share structures
                """,
                metadata={"source": "Legal Compliance Guide", "type": "compliance"}
            ),
            
            # Document Templates
            Document(
                page_content="""
                ADGM Document Templates and Standards:
                
                Articles of Association Template:
                - Company name and registered office
                - Objects clause with ADGM jurisdiction
                - Share capital structure
                - Director appointment procedures
                - Shareholder rights and meetings
                
                Memorandum of Association Template:
                - Company name and type
                - Registered office address
                - Objects and powers
                - Liability of members
                - Capital structure
                
                Board Resolution Template:
                - Meeting date and location
                - Directors present
                - Resolution text
                - Voting results
                - Signature blocks
                
                UBO Declaration Template:
                - Ultimate beneficial owner details
                - Ownership percentages
                - Control structures
                - Declaration statements
                - Supporting documentation
                """,
                metadata={"source": "ADGM Templates", "type": "template"}
            )
        ]
        
        return knowledge_base
    
    def _initialize_vector_store(self):
        """Initialize the TF-IDF vector store with ADGM knowledge."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Split documents into chunks
        self.texts = []
        self.documents = []
        for doc in self.adgm_knowledge:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                self.texts.append(chunk)
                self.documents.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))
        
        # Create TF-IDF matrix
        if self.texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)
    
    def get_relevant_context(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant ADGM legal context for a query using TF-IDF similarity."""
        if not hasattr(self, 'tfidf_matrix') or self.tfidf_matrix is None:
            raise ValueError("Vector store not initialized")
        
        # Transform query to TF-IDF
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top k most similar documents
        top_indices = similarities.argsort()[-k:][::-1]
        
        return [self.documents[i] for i in top_indices]
    
    def analyze_document_compliance(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Analyze document compliance with ADGM regulations."""
        query = f"""
        Analyze the following {document_type} for ADGM compliance:
        
        Document Type: {document_type}
        Document Content: {document_text[:2000]}...
        
        Please identify:
        1. Compliance issues and red flags
        2. Missing required sections
        3. Jurisdiction problems
        4. Specific ADGM regulation violations
        5. Suggestions for improvement
        
        Provide specific references to ADGM regulations where applicable.
        """
        
        # Get relevant context
        context_docs = self.get_relevant_context(query)
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Generate analysis using LLM
        prompt = f"""
        Based on the following ADGM legal context and the document analysis request:
        
        ADGM Context:
        {context}
        
        Analysis Request:
        {query}
        
        Please provide a structured analysis in JSON format with the following fields:
        - compliance_issues: List of compliance problems found
        - red_flags: List of red flags identified
        - missing_sections: List of missing required sections
        - jurisdiction_issues: List of jurisdiction-related problems
        - suggestions: List of improvement suggestions
        - adgm_references: List of specific ADGM regulation references
        - severity: Overall severity level (Low/Medium/High)
        """
        
        response = self.llm.predict(prompt)
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback to structured text analysis
            analysis = {
                "compliance_issues": [],
                "red_flags": [],
                "missing_sections": [],
                "jurisdiction_issues": [],
                "suggestions": [],
                "adgm_references": [],
                "severity": "Medium",
                "raw_response": response
            }
        
        return analysis
    
    def generate_legal_suggestions(self, issue: str, document_type: str) -> str:
        """Generate legal suggestions for specific issues."""
        query = f"Provide ADGM-compliant suggestions for {issue} in {document_type}"
        
        context_docs = self.get_relevant_context(query)
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""
        Based on ADGM regulations, provide specific suggestions for the following issue:
        
        Issue: {issue}
        Document Type: {document_type}
        
        ADGM Context:
        {context}
        
        Please provide:
        1. Specific ADGM regulation reference
        2. Compliant clause wording
        3. Implementation guidance
        """
        
        response = self.llm.predict(prompt)
        return response
    
    def validate_jurisdiction_clauses(self, text: str) -> Dict[str, Any]:
        """Validate jurisdiction clauses for ADGM compliance."""
        query = "ADGM jurisdiction clauses compliance requirements"
        context_docs = self.get_relevant_context(query)
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""
        Analyze the following text for ADGM jurisdiction compliance:
        
        Text: {text}
        
        ADGM Context:
        {context}
        
        Check for:
        1. References to UAE Federal Courts (should be ADGM)
        2. Correct governing law clauses
        3. ADGM-specific jurisdiction language
        4. Compliance with ADGM Companies Regulations
        
        Provide specific issues and corrections.
        """
        
        response = self.llm.predict(prompt)
        return {"analysis": response, "context": context}
    
    def get_adgm_reference(self, topic: str) -> str:
        """Get specific ADGM regulation reference for a topic."""
        query = f"ADGM regulations for {topic}"
        context_docs = self.get_relevant_context(query)
        
        if context_docs:
            return context_docs[0].page_content
        return f"No specific ADGM reference found for {topic}"
