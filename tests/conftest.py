# File: tests/conftest.py
"""
Pytest configuration and shared fixtures.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from provenanceai.core.schema import (
    ProvenanceReport,
    ProvenanceBlock,
    IdentityBlock,
    TrustScore,
    DocumentType,
    ReviewStatus,
    LicenseType,
    AIUsagePermission,
)


@pytest.fixture
def benchmark():
    """Fallback benchmark fixture when pytest-benchmark is not installed."""

    def _runner(func, *args, **kwargs):
        return func(*args, **kwargs)

    return _runner


@pytest.fixture
def sample_text_file():
    """Create a temporary text file with sample content."""
    content = """Test Research Paper on AI Ethics
Authors: Dr. Jane Smith, Dr. John Doe
Institution: University of Oxford, AI Ethics Research Center
Date: 2023-06-15
DOI: 10.1000/xyz123

ABSTRACT
This paper explores ethical considerations in AI systems...
Keywords: AI Ethics, Machine Learning, Fairness

INTRODUCTION
Artificial Intelligence systems are increasingly...

REFERENCES
1. Smith, J. (2022). Ethical AI. Journal of Ethics.
2. Doe, J. (2021). Fair ML. Proceedings of AI Conference.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_pdf_metadata():
    """Sample PDF metadata for testing."""
    return {
        'filename': 'research_paper.pdf',
        'file_size_bytes': 1024000,
        'page_count': 12,
        'author': 'Dr. Jane Smith; Dr. John Doe',
        'title': 'Test Research Paper on AI Ethics',
        'subject': 'AI Ethics Research',
        'keywords': 'AI Ethics; Machine Learning; Fairness',
        'creator': 'LaTeX',
        'producer': 'pdfTeX-1.40.0',
        'creationDate': "D:20230615000000",
    }


@pytest.fixture
def sample_docx_metadata():
    """Sample DOCX metadata for testing."""
    return {
        'filename': 'technical_report.docx',
        'file_size_bytes': 512000,
        'author': 'Technical Team',
        'title': 'Quarterly Technical Report Q2 2023',
        'subject': 'Technical Documentation',
        'keywords': 'report; technical; quarterly',
        'created': datetime(2023, 6, 15),
        'modified': datetime(2023, 6, 20),
        'last_modified_by': 'Editor',
        'paragraph_count': 45,
    }


@pytest.fixture
def sample_provenance_block():
    """Sample provenance block for testing."""
    return ProvenanceBlock(
        document_type=DocumentType.RESEARCH_PAPER,
        title="Test Research Paper on AI Ethics",
        authors=["Dr. Jane Smith", "Dr. John Doe"],
        institutions=["University of Oxford", "AI Ethics Research Center"],
        publication_date=datetime(2023, 6, 15),
        retrieved_date=datetime(2023, 12, 1),
        review_status=ReviewStatus.PEER_REVIEWED,
        citation="Smith, J. & Doe, J. (2023). Test Research Paper on AI Ethics."
    )


@pytest.fixture
def sample_trust_scores():
    """Sample trust scores for testing."""
    return {
        'authority': TrustScore(
            score=0.85,
            confidence=0.8,
            dimensions={'institution_authority': 0.9, 'author_credentials': 0.8},
            explanation="High authority from academic institution",
            rule_applied="academic_institution_check"
        ),
        'document_type': TrustScore(
            score=0.9,
            confidence=0.9,
            dimensions={'document_type': 0.9},
            explanation="Research paper type indicates high trust",
            rule_applied="document_type_mapping"
        ),
        'overall': TrustScore(
            score=0.82,
            confidence=0.8,
            dimensions={'authority': 0.85, 'document_type': 0.9, 'review': 0.8, 'currency': 0.75},
            explanation="Weighted average of dimension scores",
            rule_applied="weighted_average"
        )
    }


@pytest.fixture
def sample_config_yaml():
    """Sample YAML configuration for testing."""
    config = """
trust_scoring:
  weights:
    authority: 0.35
    document_type: 0.25
    review: 0.20
    currency: 0.10
    completeness: 0.10
  
  document_type_scores:
    research_paper: 0.95
    government_document: 0.90
    blog_post: 0.20
  
  review_scores:
    peer_reviewed: 0.95
    self_published: 0.30

policy:
  license_mappings:
    government_document: public_domain
    arxiv_preprint: CC_BY
  
  trust_thresholds:
    high_trust: 0.80
    medium_trust: 0.60
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config)
        temp_path = Path(f.name)
    
    yield temp_path
    
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_document_loader():
    """Mock document loader for unit testing."""
    mock = Mock()
    mock.load_document.return_value = {
        'content': "Test document content",
        'metadata': {
            'filename': 'test.pdf',
            'file_size_bytes': 1000,
            'mime_type': 'application/pdf',
            'author': 'Test Author',
            'title': 'Test Document',
        }
    }
    return mock