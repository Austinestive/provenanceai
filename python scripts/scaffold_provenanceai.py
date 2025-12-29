#!/usr/bin/env python3
"""
ProvenanceAI Project Scaffolding Script
Creates the complete project structure with all required files.
Run: python scaffold_provenanceai.py
"""

import os
import sys
from pathlib import Path

def create_file(path, content=""):
    """Create a file with given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {path}")

def create_project_structure(base_dir):
    """Create the complete ProvenanceAI project structure."""
    base_path = Path(base_dir)
    
    # Core source structure
    dirs_to_create = [
        # Source layout (PEP 420)
        base_path / "src" / "provenanceai",
        base_path / "src" / "provenanceai" / "core",
        base_path / "src" / "provenanceai" / "ingestion",
        base_path / "src" / "provenanceai" / "inference",
        base_path / "src" / "provenanceai" / "trust",
        base_path / "src" / "provenanceai" / "policy",
        base_path / "src" / "provenanceai" / "integration",
        base_path / "src" / "provenanceai" / "utils",
        
        # Tests
        base_path / "tests" / "unit",
        base_path / "tests" / "integration",
        base_path / "tests" / "fixtures",
        
        # Documentation
        base_path / "docs" / "source",
        base_path / "docs" / "source" / "api",
        
        # Configuration
        base_path / "config",
        
        # Examples
        base_path / "examples" / "rag_integration",
        base_path / "examples" / "basic_usage",
        
        # Data for tests
        base_path / "data" / "test_documents",
    ]
    
    # Create directories
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    # Create __init__.py files for proper package structure
    init_files = [
        base_path / "src" / "provenanceai" / "__init__.py",
        base_path / "src" / "provenanceai" / "core" / "__init__.py",
        base_path / "src" / "provenanceai" / "ingestion" / "__init__.py",
        base_path / "src" / "provenanceai" / "inference" / "__init__.py",
        base_path / "src" / "provenanceai" / "trust" / "__init__.py",
        base_path / "src" / "provenanceai" / "policy" / "__init__.py",
        base_path / "src" / "provenanceai" / "integration" / "__init__.py",
        base_path / "src" / "provenanceai" / "utils" / "__init__.py",
    ]
    
    for init_file in init_files:
        create_file(init_file, '# Auto-generated __init__.py\n\n"""ProvenanceAI module."""\n')

    # 1. Core Schema Module
    create_file(
        base_path / "src" / "provenanceai" / "core" / "schema.py",
        '''"""
Core schema definitions for ProvenanceAI.
Python dataclasses with JSON serialization support.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
import json
from uuid import uuid4


class DocumentType(str, Enum):
    """Standard document types with provenance implications."""
    RESEARCH_PAPER = "research_paper"
    TECHNICAL_REPORT = "technical_report"
    GOVERNMENT_DOCUMENT = "government_document"
    NEWSPAPER_ARTICLE = "newspaper_article"
    BLOG_POST = "blog_post"
    CONFERENCE_PAPER = "conference_paper"
    PREPRINT = "preprint"
    THESIS = "thesis"
    PATENT = "patent"
    LEGAL_DOCUMENT = "legal_document"
    WIKIPEDIA_ENTRY = "wikipedia_entry"
    STANDARD = "standard"
    UNKNOWN = "unknown"


class ReviewStatus(str, Enum):
    """Peer review status."""
    PEER_REVIEWED = "peer_reviewed"
    EDITOR_REVIEWED = "editor_reviewed"
    SELF_PUBLISHED = "self_published"
    UNREVIEWED = "unreviewed"


class LicenseType(str, Enum):
    """Common content licenses."""
    CC_BY = "CC-BY"
    CC_BY_NC = "CC-BY-NC"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC_SA = "CC-BY-NC-SA"
    CC0 = "CC0"
    COPYRIGHTED = "copyrighted"
    PUBLIC_DOMAIN = "public_domain"
    UNKNOWN = "unknown"


class AIUsagePermission(str, Enum):
    """Permissions for AI usage."""
    ALLOWED = "allowed"
    ATTRIBUTION_REQUIRED = "attribution_required"
    NON_COMMERCIAL_ONLY = "non_commercial_only"
    NO_TRAINING = "no_training"
    NO_QUOTING = "no_quoting"
    NO_SUMMARIZATION = "no_summarization"
    PROHIBITED = "prohibited"


@dataclass
class IdentityBlock:
    """Identity information block."""
    document_id: str = field(default_factory=lambda: str(uuid4()))
    original_filename: Optional[str] = None
    file_hash: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProvenanceBlock:
    """Provenance information block."""
    document_type: Optional[DocumentType] = None
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    publishers: List[str] = field(default_factory=list)
    publication_date: Optional[datetime] = None
    retrieved_date: Optional[datetime] = None
    version: Optional[str] = None
    review_status: Optional[ReviewStatus] = None
    citation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert datetime to ISO format for JSON serialization
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result


@dataclass
class ContentBlock:
    """Content analysis block."""
    language: Optional[str] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    has_references: Optional[bool] = None
    has_citations: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrustScore:
    """Individual trust score with explanation."""
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    dimensions: Dict[str, float]  # e.g., {"authority": 0.8, "currency": 0.6}
    explanation: str  # Human-readable explanation
    rule_applied: Optional[str] = None  # Which rule generated this score
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrustBlock:
    """Trust assessment block."""
    overall_score: Optional[TrustScore] = None
    authority_score: Optional[TrustScore] = None
    document_type_score: Optional[TrustScore] = None
    review_score: Optional[TrustScore] = None
    currency_score: Optional[TrustScore] = None
    completeness_score: Optional[TrustScore] = None
    custom_scores: Dict[str, TrustScore] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                elif isinstance(value, dict):
                    result[key] = {k: v.to_dict() if hasattr(v, 'to_dict') else v 
                                  for k, v in value.items()}
        return result


@dataclass
class AIUseBlock:
    """AI usage policy block."""
    license: Optional[LicenseType] = None
    attribution_required: bool = False
    commercial_use_allowed: bool = True
    allowed_actions: List[AIUsagePermission] = field(default_factory=list)
    prohibited_actions: List[AIUsagePermission] = field(default_factory=list)
    attribution_text: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplainabilityBlock:
    """Explainability and transparency block."""
    inference_sources: List[str] = field(default_factory=list)  # How each field was determined
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    assumptions_made: List[str] = field(default_factory=list)
    metadata_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TechnicalBlock:
    """Technical metadata block."""
    schema_version: str = "1.0.0"
    processing_timestamp: datetime = field(default_factory=datetime.utcnow)
    processor_version: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert datetime to ISO format
        if isinstance(result.get('processing_timestamp'), datetime):
            result['processing_timestamp'] = result['processing_timestamp'].isoformat()
        return result


@dataclass
class ProvenanceReport:
    """
    Complete provenance report for a document.
    This is the main output of the ProvenanceAI system.
    """
    identity: IdentityBlock = field(default_factory=IdentityBlock)
    provenance: ProvenanceBlock = field(default_factory=ProvenanceBlock)
    content: ContentBlock = field(default_factory=ContentBlock)
    trust: TrustBlock = field(default_factory=TrustBlock)
    ai_use: AIUseBlock = field(default_factory=AIUseBlock)
    explainability: ExplainabilityBlock = field(default_factory=ExplainabilityBlock)
    technical: TechnicalBlock = field(default_factory=TechnicalBlock)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire report to a dictionary."""
        return {
            'identity': self.identity.to_dict(),
            'provenance': self.provenance.to_dict(),
            'content': self.content.to_dict(),
            'trust': self.trust.to_dict(),
            'ai_use': self.ai_use.to_dict(),
            'explainability': self.explainability.to_dict(),
            'technical': self.technical.to_dict(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize the report to JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceReport':
        """Create a report from a dictionary."""
        # This is a simplified version - would need full implementation
        return cls()
'''
    )

    # 2. Document Ingestion Module
    create_file(
        base_path / "src" / "provenanceai" / "ingestion" / "document_loader.py",
        '''"""
Document ingestion module.
Supports multiple file formats with consistent metadata extraction.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO, Union
import hashlib
import mimetypes


class DocumentLoader:
    """Base document loader with common functionality."""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.html': 'text/html',
        '.htm': 'text/html',
    }
    
    def __init__(self):
        self.mime_types = mimetypes.MimeTypes()
    
    def can_load(self, file_path: Union[str, Path]) -> bool:
        """Check if this loader can handle the given file."""
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def calculate_file_hash(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA-256 hash of file."""
        path = Path(file_path)
        sha256_hash = hashlib.sha256()
        
        with open(path, 'rb') as f:
            # Read file in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def extract_basic_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract basic file metadata."""
        path = Path(file_path)
        
        return {
            'filename': path.name,
            'file_extension': path.suffix.lower(),
            'file_size_bytes': path.stat().st_size,
            'created_timestamp': path.stat().st_ctime,
            'modified_timestamp': path.stat().st_mtime,
            'absolute_path': str(path.absolute()),
        }
    
    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load document and extract both content and metadata.
        
        Returns:
            Dictionary with 'content' and 'metadata' keys
        """
        raise NotImplementedError("Subclasses must implement load_document")
    
    def get_mime_type(self, file_path: Union[str, Path]) -> str:
        """Get MIME type of file."""
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(str(path))
        
        if mime_type:
            return mime_type
        
        # Fallback to our mapping
        return self.SUPPORTED_EXTENSIONS.get(
            path.suffix.lower(), 
            'application/octet-stream'
        )


class TextDocumentLoader(DocumentLoader):
    """Loader for plain text documents."""
    
    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        path = Path(file_path)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        metadata = self.extract_basic_metadata(path)
        metadata.update({
            'mime_type': self.get_mime_type(path),
            'file_hash': self.calculate_file_hash(path),
            'character_count': len(content),
            'line_count': content.count('\\n') + 1,
        })
        
        return {
            'content': content,
            'metadata': metadata,
        }


class PDFDocumentLoader(DocumentLoader):
    """Loader for PDF documents."""
    
    def __init__(self):
        super().__init__()
        # Lazy import to avoid dependency if not used
        self._pymupdf = None
    
    def _ensure_pymupdf(self):
        """Ensure PyMuPDF is available."""
        if self._pymupdf is None:
            try:
                import fitz  # PyMuPDF
                self._pymupdf = fitz
            except ImportError:
                raise ImportError(
                    "PyMuPDF (fitz) is required for PDF loading. "
                    "Install with: pip install pymupdf"
                )
    
    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        self._ensure_pymupdf()
        path = Path(file_path)
        
        doc = self._pymupdf.open(str(path))
        
        # Extract text from all pages
        content_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            content_parts.append(page.get_text())
        
        content = '\\n\\n'.join(content_parts)
        
        # Extract metadata from PDF info
        pdf_metadata = doc.metadata
        
        metadata = self.extract_basic_metadata(path)
        metadata.update({
            'mime_type': 'application/pdf',
            'file_hash': self.calculate_file_hash(path),
            'pdf_metadata': pdf_metadata,
            'page_count': len(doc),
            'author': pdf_metadata.get('author'),
            'title': pdf_metadata.get('title'),
            'subject': pdf_metadata.get('subject'),
            'keywords': pdf_metadata.get('keywords'),
            'creator': pdf_metadata.get('creator'),
            'producer': pdf_metadata.get('producer'),
            'creation_date': pdf_metadata.get('creationDate'),
            'modification_date': pdf_metadata.get('modDate'),
        })
        
        doc.close()
        
        return {
            'content': content,
            'metadata': metadata,
        }


class DOCXDocumentLoader(DocumentLoader):
    """Loader for DOCX documents."""
    
    def __init__(self):
        super().__init__()
        self._python_docx = None
    
    def _ensure_python_docx(self):
        """Ensure python-docx is available."""
        if self._python_docx is None:
            try:
                import docx
                self._python_docx = docx
            except ImportError:
                raise ImportError(
                    "python-docx is required for DOCX loading. "
                    "Install with: pip install python-docx"
                )
    
    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        self._ensure_python_docx()
        path = Path(file_path)
        
        doc = self._python_docx.Document(str(path))
        
        # Extract text from all paragraphs
        content_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content_parts.append(paragraph.text)
        
        content = '\\n\\n'.join(content_parts)
        
        # Extract core properties
        core_props = doc.core_properties
        
        metadata = self.extract_basic_metadata(path)
        metadata.update({
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_hash': self.calculate_file_hash(path),
            'author': core_props.author,
            'title': core_props.title,
            'subject': core_props.subject,
            'keywords': core_props.keywords,
            'last_modified_by': core_props.last_modified_by,
            'created': core_props.created,
            'modified': core_props.modified,
            'category': core_props.category,
            'comments': core_props.comments,
            'paragraph_count': len(content_parts),
        })
        
        return {
            'content': content,
            'metadata': metadata,
        }


class DocumentLoaderFactory:
    """Factory for creating appropriate document loaders."""
    
    LOADERS = {
        '.pdf': PDFDocumentLoader,
        '.docx': DOCXDocumentLoader,
        '.txt': TextDocumentLoader,
        '.md': TextDocumentLoader,
        '.html': TextDocumentLoader,
        '.htm': TextDocumentLoader,
    }
    
    @classmethod
    def get_loader(cls, file_path: Union[str, Path]) -> DocumentLoader:
        """Get appropriate loader for file type."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        loader_class = cls.LOADERS.get(extension)
        if loader_class is None:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return loader_class()
    
    @classmethod
    def load_document(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load document using appropriate loader."""
        loader = cls.get_loader(file_path)
        return loader.load_document(file_path)
'''
    )

    # 3. Provenance Inference Module
    create_file(
        base_path / "src" / "provenanceai" / "inference" / "provenance_inferencer.py",
        '''"""
Provenance inference module.
Uses heuristics and NER to infer provenance information.
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import asdict

from ..core.schema import (
    ProvenanceBlock,
    DocumentType,
    ReviewStatus,
    ExplainabilityBlock,
)


class ProvenanceInferencer:
    """Infers provenance information from document content and metadata."""
    
    # Patterns for inference
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
    URL_PATTERN = r'https?://[^\\s]+'
    DOI_PATTERN = r'10\\.\\d{4,9}/[-._;()/:A-Z0-9]+'
    ARXIV_PATTERN = r'arXiv:\\d{4}\\.\\d{4,5}(v\\d+)?'
    DATE_PATTERNS = [
        r'\\d{4}-\\d{2}-\\d{2}',  # YYYY-MM-DD
        r'\\d{2}/\\d{2}/\\d{4}',  # MM/DD/YYYY
        r'\\d{4}',  # Just year
    ]
    
    def __init__(self):
        self.inference_sources = []
        self.confidence_scores = {}
        self.warnings = []
    
    def infer_from_metadata(self, 
                           content: str, 
                           metadata: Dict[str, Any]) -> Tuple[ProvenanceBlock, ExplainabilityBlock]:
        """
        Infer provenance information from document content and metadata.
        
        Returns:
            Tuple of (ProvenanceBlock, ExplainabilityBlock)
        """
        provenance = ProvenanceBlock()
        explainability = ExplainabilityBlock()
        
        # Document type inference
        doc_type, doc_type_source = self._infer_document_type(content, metadata)
        provenance.document_type = doc_type
        self._record_inference('document_type', doc_type_source)
        
        # Author inference
        authors, author_source = self._infer_authors(content, metadata)
        provenance.authors = authors
        self._record_inference('authors', author_source)
        
        # Institution inference
        institutions, inst_source = self._infer_institutions(content, metadata)
        provenance.institutions = institutions
        self._record_inference('institutions', inst_source)
        
        # Date inference
        pub_date, date_source = self._infer_publication_date(content, metadata)
        provenance.publication_date = pub_date
        self._record_inference('publication_date', date_source)
        
        # Title inference
        title, title_source = self._infer_title(content, metadata)
        provenance.title = title
        self._record_inference('title', title_source)
        
        # Review status inference
        review_status, review_source = self._infer_review_status(content, metadata, doc_type)
        provenance.review_status = review_status
        self._record_inference('review_status', review_source)
        
        # Citation inference
        citation, citation_source = self._infer_citation(provenance)
        provenance.citation = citation
        self._record_inference('citation', citation_source)
        
        # Set retrieved date to now
        provenance.retrieved_date = datetime.utcnow()
        
        # Update explainability block
        explainability.inference_sources = self.inference_sources
        explainability.confidence_scores = self.confidence_scores.copy()
        explainability.warnings = self.warnings.copy()
        
        return provenance, explainability
    
    def _infer_document_type(self, content: str, metadata: Dict[str, Any]) -> Tuple[Optional[DocumentType], str]:
        """Infer document type from content and metadata."""
        text_lower = content.lower()
        metadata_lower = {k: str(v).lower() for k, v in metadata.items() if v}
        
        # Check for arXiv patterns
        if re.search(self.ARXIV_PATTERN, content, re.IGNORECASE):
            return DocumentType.PREPRINT, "arxiv_id_detected"
        
        # Check for DOI
        if re.search(self.DOI_PATTERN, content):
            # Check if it's a thesis by common patterns
            if any(word in text_lower for word in ['thesis', 'dissertation', 'phd']):
                return DocumentType.THESIS, "doi_with_thesis_keywords"
            return DocumentType.RESEARCH_PAPER, "doi_detected"
        
        # Check for legal document patterns
        legal_terms = ['case no', 'v.', 'plaintiff', 'defendant', 'court', 'legal']
        if any(term in text_lower for term in legal_terms):
            return DocumentType.LEGAL_DOCUMENT, "legal_terminology"
        
        # Check metadata for clues
        if 'pdf_metadata' in metadata:
            pdf_meta = metadata['pdf_metadata']
            if pdf_meta.get('keywords', ''):
                keywords = pdf_meta['keywords'].lower()
                if 'patent' in keywords:
                    return DocumentType.PATENT, "pdf_keywords"
        
        # Check file name for clues
        filename = metadata.get('filename', '').lower()
        if 'report' in filename:
            return DocumentType.TECHNICAL_REPORT, "filename_pattern"
        elif 'patent' in filename:
            return DocumentType.PATENT, "filename_pattern"
        
        return DocumentType.UNKNOWN, "no_strong_indicators"
    
    def _infer_authors(self, content: str, metadata: Dict[str, Any]) -> Tuple[List[str], str]:
        """Infer authors from content and metadata."""
        authors = []
        source = "metadata_extraction"
        
        # First, check metadata
        if metadata.get('author'):
            authors.append(metadata['author'])
            source = "metadata_author_field"
        
        # Check PDF metadata
        if 'pdf_metadata' in metadata and metadata['pdf_metadata'].get('author'):
            pdf_author = metadata['pdf_metadata']['author']
            if pdf_author not in authors:
                authors.append(pdf_author)
                source = "pdf_metadata"
        
        # Try to extract from first few lines of content
        if not authors:
            first_lines = content[:1000].split('\\n')
            for line in first_lines[:10]:  # Check first 10 lines
                line_lower = line.lower()
                if any(term in line_lower for term in ['author', 'by ', 'written by']):
                    # Simple extraction - in real implementation would use NER
                    authors.append(line.strip())
                    source = "content_analysis"
                    break
        
        return authors, source
    
    def _infer_institutions(self, content: str, metadata: Dict[str, Any]) -> Tuple[List[str], str]:
        """Infer institutions from content and metadata."""
        institutions = []
        source = "no_institutions_found"
        
        # Common institution patterns
        institution_keywords = [
            'university', 'college', 'institute', 'laboratory', 'lab',
            'center for', 'department of', 'school of',
            'corporation', 'inc.', 'ltd.', 'gmbh',
            'government', 'ministry', 'agency'
        ]
        
        # Check first few paragraphs
        paragraphs = content.split('\\n\\n')[:5]
        for para in paragraphs:
            para_lower = para.lower()
            for keyword in institution_keywords:
                if keyword in para_lower:
                    # Extract the institution name (simplified)
                    institutions.append(para.strip()[:100])  # First 100 chars
                    source = "keyword_matching"
                    break
        
        # Check email domains for institutions
        email_matches = re.findall(self.EMAIL_PATTERN, content)
        for email in email_matches[:5]:  # Limit to first 5 emails
            domain = email.split('@')[1]
            # Check if domain looks like an institution
            if any(edu in domain for edu in ['.edu', '.ac.', '.gov']):
                institutions.append(domain)
                source = "email_domain_analysis"
        
        return list(set(institutions)), source
    
    def _infer_publication_date(self, content: str, metadata: Dict[str, Any]) -> Tuple[Optional[datetime], str]:
        """Infer publication date from content and metadata."""
        source = "no_date_found"
        
        # Check metadata first
        date_fields = ['created', 'modified', 'creation_date', 'modification_date']
        for field in date_fields:
            if field in metadata and metadata[field]:
                try:
                    # Parse date - implementation depends on format
                    # This is a simplified version
                    return datetime.fromisoformat(str(metadata[field])[:10]), f"metadata_{field}"
                except (ValueError, TypeError):
                    continue
        
        # Search for date patterns in content
        first_1000_chars = content[:1000]
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, first_1000_chars)
            if matches:
                try:
                    date_str = matches[0]
                    if len(date_str) == 4:  # Just year
                        return datetime(int(date_str), 1, 1), "year_pattern_in_content"
                    # For other patterns, would need proper parsing
                except ValueError:
                    continue
        
        return None, source
    
    def _infer_title(self, content: str, metadata: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """Infer title from content and metadata."""
        source = "no_title_found"
        
        # Check metadata first
        if metadata.get('title'):
            return metadata['title'], "metadata_title_field"
        
        if 'pdf_metadata' in metadata and metadata['pdf_metadata'].get('title'):
            return metadata['pdf_metadata']['title'], "pdf_metadata"
        
        # Try to extract from first line
        first_line = content.split('\\n')[0].strip()
        if len(first_line) < 200 and len(first_line) > 10:  # Reasonable title length
            return first_line, "first_line_extraction"
        
        return None, source
    
    def _infer_review_status(self, 
                            content: str, 
                            metadata: Dict[str, Any],
                            doc_type: Optional[DocumentType]) -> Tuple[Optional[ReviewStatus], str]:
        """Infer review status from content, metadata, and document type."""
        
        if doc_type == DocumentType.PREPRINT:
            return ReviewStatus.UNREVIEWED, "preprint_implication"
        
        text_lower = content.lower()
        
        # Check for peer review mentions
        if any(term in text_lower for term in [
            'peer-reviewed', 'reviewed by', 'refereed',
            'this paper was reviewed'
        ]):
            return ReviewStatus.PEER_REVIEWED, "explicit_peer_review_mention"
        
        # Check for journal indicators
        journal_indicators = ['journal of', 'vol.', 'no.', 'pp.', 'doi.org']
        if any(indicator in text_lower for indicator in journal_indicators):
            return ReviewStatus.PEER_REVIEWED, "journal_formatting"
        
        # Check for blog indicators
        blog_indicators = ['posted on', 'blog', 'medium.com']
        if any(indicator in text_latter for indicator in blog_indicators):
            return ReviewStatus.SELF_PUBLISHED, "blog_formatting"
        
        return ReviewStatus.UNREVIEWED, "default_unreviewed"
    
    def _infer_citation(self, provenance: ProvenanceBlock) -> Tuple[Optional[str], str]:
        """Generate citation from provenance information."""
        if not provenance.authors or not provenance.title:
            return None, "insufficient_data"
        
        # Simple citation format: Authors (Year) Title
        authors_str = '; '.join(provenance.authors[:3])  # Limit to first 3 authors
        year = provenance.publication_date.year if provenance.publication_date else "n.d."
        
        citation = f"{authors_str} ({year}). {provenance.title}"
        
        if provenance.institutions:
            citation += f". {provenance.institutions[0]}"
        
        return citation, "generated_from_provenance"
    
    def _record_inference(self, field: str, source: str, confidence: float = 0.5):
        """Record inference source and confidence."""
        self.inference_sources.append(f"{field}: {source}")
        self.confidence_scores[field] = confidence
'''
    )

    # 4. Trust Scoring Engine
    create_file(
        base_path / "src" / "provenanceai" / "trust" / "scoring_engine.py",
        '''"""
Trust scoring engine.
Rule-based scoring with full explainability.
"""

from typing import Dict, Any, List, Optional
from dataclasses import asdict

from ..core.schema import (
    TrustScore,
    TrustBlock,
    DocumentType,
    ReviewStatus,
    ProvenanceBlock,
)


class TrustScoringEngine:
    """Rule-based trust scoring engine."""
    
    def __init__(self, rules_config: Optional[Dict[str, Any]] = None):
        """
        Initialize scoring engine.
        
        Args:
            rules_config: Optional configuration for scoring rules.
                         If None, uses default rules.
        """
        self.rules = rules_config or self._get_default_rules()
    
    def calculate_trust_scores(self, 
                              provenance: ProvenanceBlock,
                              content_metadata: Dict[str, Any]) -> TrustBlock:
        """
        Calculate comprehensive trust scores.
        
        Args:
            provenance: Provenance information
            content_metadata: Content analysis metadata
            
        Returns:
            TrustBlock with all scores
        """
        trust_block = TrustBlock()
        
        # Calculate individual dimension scores
        trust_block.authority_score = self._calculate_authority_score(provenance)
        trust_block.document_type_score = self._calculate_document_type_score(provenance)
        trust_block.review_score = self._calculate_review_score(provenance)
        trust_block.currency_score = self._calculate_currency_score(provenance)
        trust_block.completeness_score = self._calculate_completeness_score(
            provenance, content_metadata
        )
        
        # Calculate overall weighted score
        trust_block.overall_score = self._calculate_overall_score(trust_block)
        
        return trust_block
    
    def _calculate_authority_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate authority score based on authors and institutions."""
        score = 0.5  # Default neutral score
        dimensions = {}
        rule_applied = "default_neutral"
        
        # Institution authority rules
        if provenance.institutions:
            inst_score = 0.0
            rule_applied = "institution_analysis"
            
            for institution in provenance.institutions:
                inst_lower = institution.lower()
                
                # Government and academic institutions get higher scores
                if any(term in inst_lower for term in ['.gov', '.edu', 'university', 'college']):
                    inst_score = max(inst_score, 0.8)
                    rule_applied = "academic_gov_institution"
                elif any(term in inst_lower for term in ['inc.', 'corp', 'ltd', 'gmbh']):
                    inst_score = max(inst_score, 0.6)
                    rule_applied = "corporate_institution"
                else:
                    inst_score = max(inst_score, 0.4)
            
            dimensions['institution_authority'] = inst_score
            score = inst_score
        
        # Author count rule
        if len(provenance.authors) > 1:
            dimensions['multiple_authors'] = 0.7
            score = max(score, 0.7)
            rule_applied = "multiple_authors"
        
        # Known author patterns
        if provenance.authors:
            for author in provenance.authors:
                # Check for academic titles or degrees
                if any(title in author for title in ['Ph.D', 'Dr.', 'Professor']):
                    dimensions['author_credentials'] = 0.8
                    score = max(score, 0.8)
                    rule_applied = "author_with_credentials"
                    break
        
        explanation = f"Authority score based on {rule_applied}. "
        explanation += f"Authors: {len(provenance.authors)}, "
        explanation += f"Institutions: {len(provenance.institutions)}"
        
        return TrustScore(
            score=score,
            confidence=0.7,
            dimensions=dimensions,
            explanation=explanation,
            rule_applied=rule_applied
        )
    
    def _calculate_document_type_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on document type."""
        doc_type_scores = {
            DocumentType.RESEARCH_PAPER: 0.9,
            DocumentType.TECHNICAL_REPORT: 0.8,
            DocumentType.GOVERNMENT_DOCUMENT: 0.85,
            DocumentType.CONFERENCE_PAPER: 0.7,
            DocumentType.THESIS: 0.8,
            DocumentType.PATENT: 0.75,
            DocumentType.STANDARD: 0.85,
            DocumentType.NEWSPAPER_ARTICLE: 0.6,
            DocumentType.PREPRINT: 0.5,
            DocumentType.BLOG_POST: 0.3,
            DocumentType.WIKIPEDIA_ENTRY: 0.5,
            DocumentType.LEGAL_DOCUMENT: 0.7,
            DocumentType.UNKNOWN: 0.4,
        }
        
        doc_type = provenance.document_type or DocumentType.UNKNOWN
        score = doc_type_scores.get(doc_type, 0.5)
        
        explanation = f"Document type '{doc_type.value}' has trust score {score}"
        
        return TrustScore(
            score=score,
            confidence=0.9,
            dimensions={'document_type': score},
            explanation=explanation,
            rule_applied="document_type_mapping"
        )
    
    def _calculate_review_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on review status."""
        review_scores = {
            ReviewStatus.PEER_REVIEWED: 0.9,
            ReviewStatus.EDITOR_REVIEWED: 0.7,
            ReviewStatus.SELF_PUBLISHED: 0.4,
            ReviewStatus.UNREVIEWED: 0.3,
        }
        
        review_status = provenance.review_status or ReviewStatus.UNREVIEWED
        score = review_scores.get(review_status, 0.5)
        
        explanation = f"Review status '{review_status.value}' contributes score {score}"
        
        return TrustScore(
            score=score,
            confidence=0.8,
            dimensions={'review_status': score},
            explanation=explanation,
            rule_applied="review_status_mapping"
        )
    
    def _calculate_currency_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on document currency (age)."""
        score = 0.5
        rule_applied = "default_neutral"
        
        if provenance.publication_date:
            from datetime import datetime
            current_year = datetime.utcnow().year
            publication_year = provenance.publication_date.year
            
            age = current_year - publication_year
            
            if age <= 1:
                score = 0.9
                rule_applied = "very_recent"
            elif age <= 3:
                score = 0.8
                rule_applied = "recent"
            elif age <= 10:
                score = 0.6
                rule_applied = "moderately_old"
            else:
                score = 0.4
                rule_applied = "historical"
            
            explanation = f"Document is {age} years old ({publication_year})"
        else:
            explanation = "No publication date available"
            rule_applied = "no_date"
        
        return TrustScore(
            score=score,
            confidence=0.6 if provenance.publication_date else 0.3,
            dimensions={'currency': score},
            explanation=explanation,
            rule_applied=rule_applied
        )
    
    def _calculate_completeness_score(self, 
                                     provenance: ProvenanceBlock,
                                     content_metadata: Dict[str, Any]) -> TrustScore:
        """Calculate score based on completeness of information."""
        completeness_factors = {}
        
        # Check for key provenance fields
        fields_to_check = [
            ('authors', bool(provenance.authors)),
            ('title', bool(provenance.title)),
            ('publication_date', bool(provenance.publication_date)),
            ('institutions', bool(provenance.institutions)),
        ]
        
        present_fields = sum(1 for _, present in fields_to_check if present)
        total_fields = len(fields_to_check)
        
        field_completeness = present_fields / total_fields
        completeness_factors['provenance_fields'] = field_completeness
        
        # Check content metadata
        if content_metadata.get('has_references'):
            completeness_factors['has_references'] = 0.8
        if content_metadata.get('has_citations'):
            completeness_factors['has_citations'] = 0.7
        
        # Calculate weighted score
        if completeness_factors:
            score = sum(completeness_factors.values()) / len(completeness_factors)
        else:
            score = 0.5
        
        explanation = f"Completeness based on {len(completeness_factors)} factors. "
        explanation += f"Provenance fields: {present_fields}/{total_fields} present"
        
        return TrustScore(
            score=score,
            confidence=0.7,
            dimensions=completeness_factors,
            explanation=explanation,
            rule_applied="completeness_analysis"
        )
    
    def _calculate_overall_score(self, trust_block: TrustBlock) -> TrustScore:
        """Calculate overall weighted trust score."""
        weights = {
            'authority': 0.3,
            'document_type': 0.2,
            'review': 0.25,
            'currency': 0.15,
            'completeness': 0.1,
        }
        
        scores = {
            'authority': trust_block.authority_score.score if trust_block.authority_score else 0.5,
            'document_type': trust_block.document_type_score.score if trust_block.document_type_score else 0.5,
            'review': trust_block.review_score.score if trust_block.review_score else 0.5,
            'currency': trust_block.currency_score.score if trust_block.currency_score else 0.5,
            'completeness': trust_block.completeness_score.score if trust_block.completeness_score else 0.5,
        }
        
        # Weighted average
        weighted_sum = sum(scores[dim] * weight for dim, weight in weights.items())
        total_weight = sum(weights.values())
        overall_score = weighted_sum / total_weight
        
        # Confidence is average of confidences
        confidences = [
            trust_block.authority_score.confidence if trust_block.authority_score else 0.5,
            trust_block.document_type_score.confidence if trust_block.document_type_score else 0.5,
            trust_block.review_score.confidence if trust_block.review_score else 0.5,
            trust_block.currency_score.confidence if trust_block.currency_score else 0.5,
            trust_block.completeness_score.confidence if trust_block.completeness_score else 0.5,
        ]
        overall_confidence = sum(confidences) / len(confidences)
        
        explanation = "Overall trust score calculated as weighted average of: "
        explanation += ", ".join(f"{dim}({scores[dim]:.2f}*{weights[dim]})" 
                                for dim in weights.keys())
        
        return TrustScore(
            score=overall_score,
            confidence=overall_confidence,
            dimensions=scores,
            explanation=explanation,
            rule_applied="weighted_average"
        )
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default scoring rules."""
        return {
            'weights': {
                'authority': 0.3,
                'document_type': 0.2,
                'review': 0.25,
                'currency': 0.15,
                'completeness': 0.1,
            },
            'document_type_scores': {
                'research_paper': 0.9,
                'government_document': 0.85,
                'technical_report': 0.8,
                'thesis': 0.8,
                'conference_paper': 0.7,
                'patent': 0.75,
                'newspaper_article': 0.6,
                'preprint': 0.5,
                'blog_post': 0.3,
                'unknown': 0.4,
            },
            'review_scores': {
                'peer_reviewed': 0.9,
                'editor_reviewed': 0.7,
                'self_published': 0.4,
                'unreviewed': 0.3,
            },
        }
'''
    )

    # 5. Main API Module
    create_file(
        base_path / "src" / "provenanceai" / "__init__.py",
        '''"""
ProvenanceAI - Knowledge Provenance & Trust Infrastructure for AI
"""

__version__ = "0.1.0"
__author__ = "ProvenanceAI Team"
__description__ = "A standard, explainable way for AI systems to understand provenance and trustworthiness of knowledge sources"

from .api import analyze, ProvenanceReport
from .core.schema import (
    ProvenanceReport,
    DocumentType,
    ReviewStatus,
    LicenseType,
    AIUsagePermission,
    TrustScore,
)

__all__ = [
    # Main API
    "analyze",
    "ProvenanceReport",
    
    # Core types
    "DocumentType",
    "ReviewStatus",
    "LicenseType",
    "AIUsagePermission",
    "TrustScore",
]
'''
    )

    create_file(
        base_path / "src" / "provenanceai" / "api.py",
        '''"""
Main public API for ProvenanceAI.
Provides the unified analyze() function.
"""

from pathlib import Path
from typing import Union, Optional
import json

from .core.schema import ProvenanceReport
from .ingestion.document_loader import DocumentLoaderFactory
from .inference.provenance_inferencer import ProvenanceInferencer
from .trust.scoring_engine import TrustScoringEngine
from .policy.ai_policy_engine import AIPolicyEngine


def analyze(file_path: Union[str, Path], 
           config_path: Optional[Union[str, Path]] = None) -> ProvenanceReport:
    """
    Main entry point for ProvenanceAI analysis.
    
    Args:
        file_path: Path to document to analyze
        config_path: Optional path to configuration file
        
    Returns:
        Complete ProvenanceReport with all analysis results
        
    Example:
        >>> from provenanceai import analyze
        >>> report = analyze("document.pdf")
        >>> print(report.to_json())
    """
    # 1. Load and validate input
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")
    
    # 2. Load configuration (simplified - would load from file)
    config = _load_config(config_path) if config_path else {}
    
    # 3. Document ingestion
    loader_result = DocumentLoaderFactory.load_document(path)
    content = loader_result['content']
    metadata = loader_result['metadata']
    
    # 4. Initialize components
    inferencer = ProvenanceInferencer()
    scoring_engine = TrustScoringEngine(config.get('trust_rules'))
    policy_engine = AIPolicyEngine(config.get('policy_rules'))
    
    # 5. Perform provenance inference
    provenance, explainability = inferencer.infer_from_metadata(content, metadata)
    
    # 6. Calculate trust scores
    content_metadata = {
        'has_references': _check_for_references(content),
        'has_citations': _check_for_citations(content),
        'word_count': len(content.split()),
    }
    trust = scoring_engine.calculate_trust_scores(provenance, content_metadata)
    
    # 7. Determine AI usage policy
    ai_use = policy_engine.determine_policy(provenance, trust)
    
    # 8. Build final report
    report = ProvenanceReport(
        identity=_build_identity_block(path, metadata),
        provenance=provenance,
        content=_build_content_block(content, metadata),
        trust=trust,
        ai_use=ai_use,
        explainability=explainability,
        technical=_build_technical_block(metadata)
    )
    
    return report


def _load_config(config_path: Union[str, Path]) -> dict:
    """Load configuration from file."""
    path = Path(config_path)
    if not path.exists():
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix.lower() == '.json':
            import json
            return json.load(f)
        elif path.suffix.lower() in ['.yaml', '.yml']:
            import yaml
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")


def _check_for_references(content: str) -> bool:
    """Check if document has references section."""
    content_lower = content.lower()
    reference_keywords = ['references', 'bibliography', 'works cited', 'sources']
    return any(keyword in content_lower for keyword in reference_keywords)


def _check_for_citations(content: str) -> bool:
    """Check if document has citations."""
    # Simple pattern matching for citations
    import re
    citation_patterns = [
        r'\\([A-Za-z]+,\\s*\\d{4}\\)',  # (Author, 2014)
        r'\\[[\\d,\\s]+\\]',  # [1, 2, 3]
        r'\\d{4}[a-z]?',  # 2014a (common in citations)
    ]
    
    for pattern in citation_patterns:
        if re.search(pattern, content):
            return True
    return False


def _build_identity_block(path: Path, metadata: dict):
    """Build identity block from file metadata."""
    from .core.schema import IdentityBlock
    from .ingestion.document_loader import DocumentLoaderFactory
    
    # Get a loader to calculate hash
    loader = DocumentLoaderFactory.get_loader(path)
    
    return IdentityBlock(
        original_filename=path.name,
        file_size_bytes=metadata.get('file_size_bytes'),
        mime_type=metadata.get('mime_type'),
        file_hash=metadata.get('file_hash', loader.calculate_file_hash(path)),
    )


def _build_content_block(content: str, metadata: dict):
    """Build content analysis block."""
    from .core.schema import ContentBlock
    from langdetect import detect
    
    try:
        language = detect(content[:1000])  # Sample first 1000 chars
    except:
        language = "unknown"
    
    return ContentBlock(
        language=language,
        word_count=len(content.split()),
        page_count=metadata.get('page_count') or metadata.get('paragraph_count'),
        keywords=metadata.get('keywords', '').split(';') if metadata.get('keywords') else [],
        has_references=_check_for_references(content),
        has_citations=_check_for_citations(content),
    )


def _build_technical_block(metadata: dict):
    """Build technical metadata block."""
    from .core.schema import TechnicalBlock
    
    return TechnicalBlock(
        processor_version="0.1.0",
        raw_metadata={k: v for k, v in metadata.items() 
                     if not isinstance(v, (bytes, type(None)))},
    )
'''
    )

    # 6. Policy Engine Module
    create_file(
        base_path / "src" / "provenanceai" / "policy" / "ai_policy_engine.py",
        '''"""
AI Usage Policy Engine.
Determines what AI may do with content based on provenance and license.
"""

from typing import Dict, Any, List, Optional
from dataclasses import asdict

from ..core.schema import (
    AIUseBlock,
    AIUsagePermission,
    LicenseType,
    ProvenanceBlock,
    TrustBlock,
    DocumentType,
)


class AIPolicyEngine:
    """Determines AI usage policies from provenance and trust information."""
    
    def __init__(self, rules_config: Optional[Dict[str, Any]] = None):
        """
        Initialize policy engine.
        
        Args:
            rules_config: Optional configuration for policy rules.
        """
        self.rules = rules_config or self._get_default_rules()
    
    def determine_policy(self, 
                        provenance: ProvenanceBlock,
                        trust: TrustBlock) -> AIUseBlock:
        """
        Determine AI usage policy based on provenance and trust.
        
        Args:
            provenance: Provenance information
            trust: Trust assessment
            
        Returns:
            AIUseBlock with permissions and restrictions
        """
        ai_use = AIUseBlock()
        
        # Determine license based on document type and provenance
        ai_use.license = self._infer_license(provenance, trust)
        
        # Set permissions based on license and trust
        self._set_permissions(ai_use, provenance, trust)
        
        # Set attribution requirements
        self._set_attribution(ai_use, provenance, trust)
        
        # Set conditions
        self._set_conditions(ai_use, provenance, trust)
        
        return ai_use
    
    def _infer_license(self, 
                      provenance: ProvenanceBlock, 
                      trust: TrustBlock) -> LicenseType:
        """Infer license from provenance and trust."""
        doc_type = provenance.document_type
        
        # Government documents are typically public domain
        if doc_type == DocumentType.GOVERNMENT_DOCUMENT:
            return LicenseType.PUBLIC_DOMAIN
        
        # Academic papers often have specific licenses
        if doc_type in [DocumentType.RESEARCH_PAPER, 
                       DocumentType.CONFERENCE_PAPER,
                       DocumentType.THESIS,
                       DocumentType.PREPRINT]:
            
            # Check for arXiv (typically CC-BY)
            import re
            if provenance.citation and 'arXiv' in provenance.citation:
                return LicenseType.CC_BY
            
            # Many academic papers are copyrighted but allow certain uses
            return LicenseType.COPYRIGHTED
        
        # Technical reports and standards often have specific terms
        if doc_type in [DocumentType.TECHNICAL_REPORT, DocumentType.STANDARD]:
            return LicenseType.COPYRIGHTED
        
        # Default to unknown
        return LicenseType.UNKNOWN
    
    def _set_permissions(self, 
                        ai_use: AIUseBlock,
                        provenance: ProvenanceBlock,
                        trust: TrustBlock):
        """Set allowed and prohibited actions."""
        # Default permissions for high-trust documents
        if trust.overall_score and trust.overall_score.score >= 0.7:
            ai_use.allowed_actions.extend([
                AIUsagePermission.ALLOWED,
                AIUsagePermission.ATTRIBUTION_REQUIRED,
            ])
            ai_use.commercial_use_allowed = True
        else:
            # More restrictive for low-trust documents
            ai_use.allowed_actions.append(AIUsagePermission.ALLOWED)
            ai_use.commercial_use_allowed = False
            ai_use.prohibited_actions.append(
                AIUsagePermission.NON_COMMERCIAL_ONLY
            )
        
        # License-specific restrictions
        if ai_use.license == LicenseType.CC_BY_NC:
            ai_use.commercial_use_allowed = False
            ai_use.prohibited_actions.append(
                AIUsagePermission.NON_COMMERCIAL_ONLY
            )
            ai_use.allowed_actions.append(
                AIUsagePermission.ATTRIBUTION_REQUIRED
            )
        
        elif ai_use.license == LicenseType.COPYRIGHTED:
            # Be conservative with copyrighted material
            ai_use.allowed_actions.extend([
                AIUsagePermission.ATTRIBUTION_REQUIRED,
                AIUsagePermission.NO_TRAINING,
            ])
            ai_use.prohibited_actions.extend([
                AIUsagePermission.NO_TRAINING,
                AIUsagePermission.NO_QUOTING,
            ])
        
        elif ai_use.license == LicenseType.PUBLIC_DOMAIN:
            # Most permissive
            ai_use.allowed_actions.extend([
                AIUsagePermission.ALLOWED,
                AIUsagePermission.ATTRIBUTION_REQUIRED,
            ])
            ai_use.commercial_use_allowed = True
    
    def _set_attribution(self,
                        ai_use: AIUseBlock,
                        provenance: ProvenanceBlock,
                        trust: TrustBlock):
        """Set attribution requirements."""
        ai_use.attribution_required = True  # Default to requiring attribution
        
        if provenance.citation:
            ai_use.attribution_text = provenance.citation
        elif provenance.title and provenance.authors:
            authors = '; '.join(provenance.authors[:3])
            year = provenance.publication_date.year if provenance.publication_date else 'n.d.'
            ai_use.attribution_text = f"{authors} ({year}). {provenance.title}"
        
        # Public domain might not require attribution
        if ai_use.license == LicenseType.PUBLIC_DOMAIN:
            ai_use.attribution_required = False
            ai_use.attribution_text = None
    
    def _set_conditions(self,
                       ai_use: AIUseBlock,
                       provenance: ProvenanceBlock,
                       trust: TrustBlock):
        """Set additional conditions for AI use."""
        conditions = []
        
        # Add trust-based conditions
        if trust.overall_score and trust.overall_score.score < 0.5:
            conditions.append("Use with caution: low trust score")
        
        # Add license conditions
        if ai_use.license == LicenseType.CC_BY:
            conditions.append("Must provide attribution")
        elif ai_use.license == LicenseType.CC_BY_NC:
            conditions.append("Non-commercial use only")
            conditions.append("Must provide attribution")
        elif ai_use.license == LicenseType.COPYRIGHTED:
            conditions.append("Copyrighted material - check specific license")
        
        # Add provenance-based conditions
        if provenance.review_status and provenance.review_status.value == 'preprint':
            conditions.append("Preprint - not peer reviewed")
        
        ai_use.conditions = conditions
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default policy rules."""
        return {
            'license_mappings': {
                'government_document': 'public_domain',
                'arxiv_preprint': 'CC_BY',
                'academic_paper': 'copyrighted',
            },
            'trust_thresholds': {
                'high_trust': 0.7,
                'medium_trust': 0.5,
                'low_trust': 0.3,
            },
            'default_permissions': {
                'high_trust': ['allowed', 'attribution_required'],
                'medium_trust': ['allowed'],
                'low_trust': ['allowed', 'non_commercial_only'],
            },
        }
'''
    )

    # 7. Configuration Files
    create_file(
        base_path / "pyproject.toml",
        '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "provenanceai"
version = "0.1.0"
description = "Knowledge Provenance & Trust Infrastructure for AI Systems"
readme = "README.md"
authors = [
    {name = "ProvenanceAI Team", email = "team@provenanceai.dev"},
]
license = {text = "Apache-2.0"}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
keywords = ["ai", "provenance", "trust", "knowledge", "rag", "metadata", "nlp"]
dependencies = [
    "pymupdf>=1.23.0",  # PDF processing
    "python-docx>=1.1.0",  # DOCX processing
    "langdetect>=1.0.9",  # Language detection
    "pydantic>=2.0.0",  # Data validation (optional for future)
    "pyyaml>=6.0",  # YAML config support
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
    "pre-commit>=3.0.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=2.0.0",
]
full = [
    "spacy>=3.0.0",  # Advanced NER
    "scikit-learn>=1.0.0",  # ML features (future)
]

[project.urls]
Homepage = "https://github.com/provenanceai/provenanceai"
Documentation = "https://provenanceai.readthedocs.io"
Repository = "https://github.com/provenanceai/provenanceai"
Issues = "https://github.com/provenanceai/provenanceai/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
provenanceai = "src/provenanceai"

[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
'''
    )

    create_file(
        base_path / "README.md",
        '''# ProvenanceAI

**Knowledge Provenance & Trust Infrastructure for AI Systems**

ProvenanceAI is a Python library that provides a standard, explainable, machine-readable way for AI systems to understand the provenance, authority, trustworthiness, and permitted use of knowledge sources.

## Why ProvenanceAI?

Modern AI systems (RAG pipelines, agents, knowledge graphs) process vast amounts of information, but they lack standardized ways to:
- Understand **where information comes from**
- Assess **how trustworthy it is**
- Know **what they're allowed to do with it**
- **Explain** their trust decisions to users

ProvenanceAI solves this by providing a library-first, framework-agnostic solution that outputs provenance metadata optimized for AI consumption.

## Key Features

- **📄 Document Ingestion**: Support for PDF, DOCX, TXT with metadata extraction
- **🔍 Provenance Inference**: Heuristic + NER-based inference of authors, institutions, dates
- **📊 Trust Scoring**: Rule-based, explainable trust scores across multiple dimensions
- **⚖️ AI Usage Policy**: License-aware determination of what AI can do with content
- **🤖 AI-Optimized Output**: JSON metadata ready for RAG pipelines and vector databases
- **🔬 Standards-Inspired**: Based on library science principles (Dublin Core, PROV-O)

## Quick Start

```python
from provenanceai import analyze

# Analyze a document
report = analyze("research_paper.pdf")

# Get JSON output for your RAG pipeline
metadata = report.to_json()
print(metadata)

# Or access structured data
print(f"Trust Score: {report.trust.overall_score.score:.2f}")
print(f"Allowed AI Actions: {report.ai_use.allowed_actions}")
    ''')

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) > 1 or (len(argv) == 1 and argv[0] in {"-h", "--help"}):
        script_name = Path(sys.argv[0]).name
        print(f"Usage: python {script_name} [output_dir]", file=sys.stderr)
        print("If output_dir is omitted, the current working directory is used.", file=sys.stderr)
        return 2

    output_dir = argv[0] if argv else os.getcwd()
    create_project_structure(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())