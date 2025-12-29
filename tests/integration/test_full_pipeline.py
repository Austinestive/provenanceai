# File: tests/integration/test_full_pipeline.py
"""
Integration tests for the complete ProvenanceAI pipeline.
"""

import pytest
from pathlib import Path
import tempfile
import json
from provenanceai import analyze
from provenanceai.core.schema import ProvenanceReport, DocumentType


class TestFullPipeline:
    """Test the complete analyze() pipeline."""
    
    def test_analyze_text_file(self):
        """Test analyzing a plain text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""Test Research Paper
By: Dr. Jane Smith, University of Oxford
Published: 2023
            
This is a test research paper about AI ethics.
References:
1. Smith, J. (2022). AI Ethics. Journal of Ethics.
""")
            temp_path = Path(f.name)
        
        try:
            report = analyze(temp_path)
            
            # Basic validation
            assert isinstance(report, ProvenanceReport)
            assert report.identity.original_filename == temp_path.name
            assert report.trust.overall_score is not None
            assert 0 <= report.trust.overall_score.score <= 1.0
            
            # JSON serialization works
            json_output = report.to_json()
            parsed = json.loads(json_output)
            assert 'identity' in parsed
            assert 'trust' in parsed
            
        finally:
            temp_path.unlink()
    
    def test_analyze_with_config(self):
        """Test analyzing with custom configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document")
            temp_path = Path(f.name)
        
        # Create config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as config_file:
            config_file.write("""
trust_scoring:
  weights:
    authority: 0.4
    document_type: 0.2
    review: 0.2
    currency: 0.1
    completeness: 0.1
""")
            config_path = Path(config_file.name)
        
        try:
            report = analyze(temp_path, config_path=config_path)
            assert isinstance(report, ProvenanceReport)
            
        finally:
            temp_path.unlink()
            config_path.unlink()
    
    def test_error_handling(self):
        """Test error handling for non-existent files."""
        with pytest.raises(FileNotFoundError):
            analyze("/non/existent/file.pdf")
        
        # Test unsupported file type
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unsupported', delete=False) as f:
            f.write("test")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError) as exc_info:
                analyze(temp_path)
            assert "Unsupported file type" in str(exc_info.value)
        
        finally:
            temp_path.unlink()


# File: tests/unit/test_schema_serialization.py
"""
Test schema serialization and deserialization.
"""

import json
from datetime import datetime
from provenanceai.core.schema import (
    ProvenanceReport, TrustScore, ProvenanceBlock,
    DocumentType, ReviewStatus
)


def test_trust_score_json_serialization():
    """Test TrustScore JSON serialization."""
    score = TrustScore(
        score=0.85,
        confidence=0.9,
        dimensions={"authority": 0.9, "currency": 0.8},
        explanation="High trust due to authoritative source",
        rule_applied="authority_check"
    )
    
    score_dict = score.to_dict()
    assert score_dict["score"] == 0.85
    assert score_dict["confidence"] == 0.9
    assert "dimensions" in score_dict
    
    # Round-trip test
    score_json = json.dumps(score_dict)
    loaded_dict = json.loads(score_json)
    assert loaded_dict["score"] == 0.85


def test_full_report_json_roundtrip():
    """Test full report JSON serialization and deserialization."""
    report = ProvenanceReport()
    report.provenance.document_type = DocumentType.RESEARCH_PAPER
    report.provenance.review_status = ReviewStatus.PEER_REVIEWED
    report.provenance.authors = ["Dr. Jane Smith"]
    report.provenance.publication_date = datetime(2023, 1, 1)
    
    # Serialize to JSON
    report_json = report.to_json()
    
    # Parse JSON
    parsed = json.loads(report_json)
    
    # Validate structure
    assert parsed["provenance"]["document_type"] == "research_paper"
    assert parsed["provenance"]["review_status"] == "peer_reviewed"
    assert parsed["provenance"]["authors"] == ["Dr. Jane Smith"]
    assert "2023-01-01" in parsed["provenance"]["publication_date"]