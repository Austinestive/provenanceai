# File: tests/unit/test_provenance_inference.py
"""
Unit tests for provenance inference module.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from provenanceai.inference.provenance_inferencer import ProvenanceInferencer
from provenanceai.core.schema import DocumentType, ReviewStatus


class TestProvenanceInferencer:
    """Test provenance inference functionality."""
    
    def test_infer_document_type(self):
        """Test document type inference."""
        inferencer = ProvenanceInferencer()
        
        # Test arXiv pattern
        content = "arXiv:2301.12345v1 This is a preprint"
        metadata = {}
        doc_type, source = inferencer._infer_document_type(content, metadata)
        assert doc_type == DocumentType.PREPRINT
        assert source == "arxiv_id_detected"
        
        # Test DOI pattern
        content = "doi:10.1000/xyz123 This is a paper"
        metadata = {}
        doc_type, source = inferencer._infer_document_type(content, metadata)
        assert doc_type == DocumentType.RESEARCH_PAPER
        assert source == "doi_detected"
        
        # Test legal document
        content = "IN THE SUPREME COURT Case No. 123 v. Defendant"
        metadata = {}
        doc_type, source = inferencer._infer_document_type(content, metadata)
        assert doc_type == DocumentType.LEGAL_DOCUMENT
        assert source == "legal_terminology"
        
        # Test unknown
        content = "Just some random text"
        metadata = {}
        doc_type, source = inferencer._infer_document_type(content, metadata)
        assert doc_type == DocumentType.UNKNOWN
        assert source == "no_strong_indicators"
    
    def test_infer_authors(self):
        """Test author inference."""
        inferencer = ProvenanceInferencer()
        
        # Test from metadata
        content = "Some content"
        metadata = {"author": "Dr. Jane Smith"}
        authors, source = inferencer._infer_authors(content, metadata)
        assert authors == ["Dr. Jane Smith"]
        assert source == "metadata_author_field"
        
        # Test from PDF metadata
        content = "Some content"
        metadata = {"pdf_metadata": {"author": "Dr. John Doe"}}
        authors, source = inferencer._infer_authors(content, metadata)
        assert authors == ["Dr. John Doe"]
        assert source == "pdf_metadata"
        
        # Test from content (first lines)
        content = "Authors: Dr. Alice, Dr. Bob\n\nAbstract..."
        metadata = {}
        authors, source = inferencer._infer_authors(content, metadata)
        assert len(authors) == 1
        assert "Authors: Dr. Alice, Dr. Bob" in authors[0]
        assert source == "content_analysis"
        
        # Test no authors found
        content = "Some content without authors"
        metadata = {}
        authors, source = inferencer._infer_authors(content, metadata)
        assert authors == []
        assert source == "metadata_extraction"
    
    def test_infer_institutions(self):
        """Test institution inference."""
        inferencer = ProvenanceInferencer()
        
        # Test from content keywords
        content = "University of Oxford research center"
        metadata = {}
        institutions, source = inferencer._infer_institutions(content, metadata)
        assert len(institutions) > 0
        assert source == "keyword_matching"
        
        # Test from email domains
        content = "Contact: researcher@oxford.ac.uk"
        metadata = {}
        institutions, source = inferencer._infer_institutions(content, metadata)
        assert any(".ac." in inst for inst in institutions)
        assert source == "email_domain_analysis"
        
        # Test no institutions
        content = "Random text without institutions"
        metadata = {}
        institutions, source = inferencer._infer_institutions(content, metadata)
        assert institutions == []
        assert source == "no_institutions_found"
    
    def test_infer_publication_date(self):
        """Test publication date inference."""
        inferencer = ProvenanceInferencer()
        
        # Test from metadata
        content = "Some content"
        metadata = {"created": "2023-06-15"}
        date, source = inferencer._infer_publication_date(content, metadata)
        assert date.year == 2023
        assert date.month == 6
        assert date.day == 15
        assert "metadata" in source
        
        # Test from content (year only)
        content = "Published in 2021. This is a paper."
        metadata = {}
        date, source = inferencer._infer_publication_date(content, metadata)
        assert date.year == 2021
        assert source == "year_pattern_in_content"
        
        # Test no date found
        content = "No date here"
        metadata = {}
        date, source = inferencer._infer_publication_date(content, metadata)
        assert date is None
        assert source == "no_date_found"
    
    def test_infer_review_status(self):
        """Test review status inference."""
        inferencer = ProvenanceInferencer()
        
        # Test peer-reviewed mentions
        content = "This paper was peer-reviewed by experts"
        metadata = {}
        doc_type = DocumentType.RESEARCH_PAPER
        status, source = inferencer._infer_review_status(content, metadata, doc_type)
        assert status == ReviewStatus.PEER_REVIEWED
        assert "peer_review" in source
        
        # Test preprint
        doc_type = DocumentType.PREPRINT
        status, source = inferencer._infer_review_status(content, metadata, doc_type)
        assert status == ReviewStatus.UNREVIEWED
        assert "preprint" in source
        
        # Test blog formatting
        content = "Posted on my blog about AI"
        metadata = {}
        doc_type = DocumentType.BLOG_POST
        status, source = inferencer._infer_review_status(content, metadata, doc_type)
        assert status == ReviewStatus.SELF_PUBLISHED
        assert "blog" in source
    
    def test_full_inference_pipeline(self):
        """Test complete inference pipeline."""
        inferencer = ProvenanceInferencer()
        
        content = """Research Paper on AI
Authors: Dr. Jane Smith (Stanford University)
Date: 2023-01-15
DOI: 10.1000/xyz123
This paper was peer-reviewed.
"""
        
        metadata = {
            "filename": "research.pdf",
            "author": "Dr. Jane Smith",
            "title": "Research Paper on AI",
        }
        
        provenance, explainability = inferencer.infer_from_metadata(content, metadata)
        
        # Check provenance fields
        assert provenance.document_type == DocumentType.RESEARCH_PAPER
        assert len(provenance.authors) > 0
        assert "Stanford" in " ".join(provenance.institutions)
        assert provenance.publication_date.year == 2023
        assert provenance.review_status == ReviewStatus.PEER_REVIEWED
        assert provenance.retrieved_date is not None
        
        # Check explainability
        assert len(explainability.inference_sources) > 0
        assert len(explainability.confidence_scores) > 0
        assert "explanation" in str(explainability).lower()