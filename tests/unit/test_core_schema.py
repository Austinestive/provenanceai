# File: tests/unit/test_core_schema.py
"""
Unit tests for core schema definitions and serialization.
"""

import json
from datetime import datetime
from decimal import Decimal
import pytest

from provenanceai.core.schema import (
    ProvenanceReport,
    ProvenanceBlock,
    IdentityBlock,
    TrustScore,
    TrustBlock,
    AIUseBlock,
    ContentBlock,
    ExplainabilityBlock,
    TechnicalBlock,
    DocumentType,
    ReviewStatus,
    LicenseType,
    AIUsagePermission,
)


class TestCoreSchema:
    """Test core schema classes."""
    
    def test_provenance_report_creation(self):
        """Test basic report creation with defaults."""
        report = ProvenanceReport()
        
        assert report.identity is not None
        assert isinstance(report.identity, IdentityBlock)
        assert report.provenance is not None
        assert isinstance(report.provenance, ProvenanceBlock)
        assert report.trust is not None
        assert isinstance(report.trust, TrustBlock)
        assert report.ai_use is not None
        assert isinstance(report.ai_use, AIUseBlock)
        assert report.explainability is not None
        assert isinstance(report.explainability, ExplainabilityBlock)
        assert report.technical is not None
        assert isinstance(report.technical, TechnicalBlock)
    
    def test_trust_score_validation(self):
        """Test TrustScore value validation."""
        # Valid scores
        score = TrustScore(score=0.75, confidence=0.8, dimensions={}, explanation="Test")
        assert score.score == 0.75
        assert score.confidence == 0.8
        
        # Score out of range should still work (but warn in production)
        score = TrustScore(score=1.5, confidence=2.0, dimensions={}, explanation="Test")
        assert score.score == 1.5
    
    def test_provenance_block_serialization(self):
        """Test ProvenanceBlock JSON serialization."""
        block = ProvenanceBlock(
            document_type=DocumentType.RESEARCH_PAPER,
            title="Test Title",
            authors=["Author 1", "Author 2"],
            publication_date=datetime(2023, 1, 15, 10, 30, 0),
            review_status=ReviewStatus.PEER_REVIEWED,
        )
        
        # Convert to dict
        block_dict = block.to_dict()
        
        # Check values
        assert block_dict["document_type"] == "research_paper"
        assert block_dict["title"] == "Test Title"
        assert block_dict["authors"] == ["Author 1", "Author 2"]
        assert "2023-01-15T10:30:00" in block_dict["publication_date"]
        assert block_dict["review_status"] == "peer_reviewed"
        
        # Round-trip through JSON
        json_str = json.dumps(block_dict)
        loaded_dict = json.loads(json_str)
        
        assert loaded_dict["document_type"] == "research_paper"
        assert loaded_dict["review_status"] == "peer_reviewed"
    
    def test_full_report_json_serialization(self):
        """Test complete report JSON serialization."""
        report = ProvenanceReport()
        
        # Populate with test data
        report.provenance.document_type = DocumentType.RESEARCH_PAPER
        report.provenance.authors = ["Dr. Jane Smith"]
        report.provenance.publication_date = datetime(2023, 1, 1)
        
        report.trust.overall_score = TrustScore(
            score=0.85,
            confidence=0.9,
            dimensions={"authority": 0.9},
            explanation="High trust",
            rule_applied="test"
        )
        
        report.ai_use.license = LicenseType.CC_BY
        report.ai_use.allowed_actions = [AIUsagePermission.ALLOWED, AIUsagePermission.ATTRIBUTION_REQUIRED]
        
        # Serialize to JSON
        json_output = report.to_json()
        
        # Validate JSON structure
        parsed = json.loads(json_output)
        
        assert "identity" in parsed
        assert "provenance" in parsed
        assert "trust" in parsed
        assert "ai_use" in parsed
        
        # Check specific values
        assert parsed["provenance"]["document_type"] == "research_paper"
        assert parsed["provenance"]["authors"] == ["Dr. Jane Smith"]
        assert parsed["ai_use"]["license"] == "CC-BY"
        assert "allowed" in parsed["ai_use"]["allowed_actions"]
        
        # Ensure no datetime objects remain (all converted to ISO strings)
        def check_no_datetime(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_datetime(v)
            elif isinstance(obj, list):
                for item in obj:
                    check_no_datetime(item)
            else:
                assert not isinstance(obj, datetime), f"Found datetime: {obj}"
        
        check_no_datetime(parsed)
    
    def test_schema_versioning(self):
        """Test schema version is included and consistent."""
        report = ProvenanceReport()
        json_output = report.to_json()
        parsed = json.loads(json_output)
        
        assert "technical" in parsed
        assert "schema_version" in parsed["technical"]
        assert parsed["technical"]["schema_version"] == "1.0.0"
    
    @pytest.mark.parametrize("document_type,expected_trust", [
        (DocumentType.RESEARCH_PAPER, 0.9),
        (DocumentType.GOVERNMENT_DOCUMENT, 0.85),
        (DocumentType.BLOG_POST, 0.3),
        (DocumentType.UNKNOWN, 0.4),
    ])
    def test_document_type_enum(self, document_type, expected_trust):
        """Test document type enum values."""
        # This test ensures our enum values are stable
        assert document_type.value == document_type.name.lower()
    
    def test_empty_lists_serialization(self):
        """Test that empty lists serialize correctly."""
        report = ProvenanceReport()
        report.provenance.authors = []
        report.provenance.institutions = []
        report.ai_use.allowed_actions = []
        
        json_output = report.to_json()
        parsed = json.loads(json_output)
        
        assert parsed["provenance"]["authors"] == []
        assert parsed["provenance"]["institutions"] == []
        assert parsed["ai_use"]["allowed_actions"] == []
    
    def test_none_handling(self):
        """Test that None values are handled properly in serialization."""
        report = ProvenanceReport()
        report.provenance.title = None
        report.provenance.publication_date = None
        
        json_output = report.to_json()
        parsed = json.loads(json_output)
        
        assert parsed["provenance"]["title"] is None
        assert parsed["provenance"]["publication_date"] is None