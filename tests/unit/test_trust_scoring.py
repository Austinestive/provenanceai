# File: tests/unit/test_trust_scoring.py
"""
Unit tests for trust scoring engine.
"""

import pytest
from datetime import datetime, timedelta

from provenanceai.trust.scoring_engine import TrustScoringEngine
from provenanceai.core.schema import (
    ProvenanceBlock,
    TrustScore,
    TrustBlock,
    DocumentType,
    ReviewStatus,
)


class TestTrustScoringEngine:
    """Test trust scoring engine functionality."""
    
    @pytest.fixture
    def scoring_engine(self):
        """Create a trust scoring engine for testing."""
        return TrustScoringEngine()
    
    @pytest.fixture
    def sample_provenance(self):
        """Create sample provenance for testing."""
        return ProvenanceBlock(
            document_type=DocumentType.RESEARCH_PAPER,
            authors=["Dr. Jane Smith", "Dr. John Doe"],
            institutions=["Stanford University", "MIT"],
            publication_date=datetime.now() - timedelta(days=180),  # 6 months old
            review_status=ReviewStatus.PEER_REVIEWED,
            title="Research Paper on AI Ethics",
        )
    
    def test_calculate_authority_score(self, scoring_engine, sample_provenance):
        """Test authority score calculation."""
        score = scoring_engine._calculate_authority_score(sample_provenance)
        
        assert isinstance(score, TrustScore)
        assert 0 <= score.score <= 1.0
        assert 0 <= score.confidence <= 1.0
        assert "dimensions" in score.to_dict()
        assert score.explanation is not None
        assert score.rule_applied is not None
        
        # Academic institutions should increase score
        assert score.score >= 0.7
    
    def test_calculate_document_type_score(self, scoring_engine, sample_provenance):
        """Test document type score calculation."""
        score = scoring_engine._calculate_document_type_score(sample_provenance)
        
        assert score.score == 0.9  # Research paper score from default rules
        assert score.explanation is not None
        
        # Test with different document types
        sample_provenance.document_type = DocumentType.BLOG_POST
        score = scoring_engine._calculate_document_type_score(sample_provenance)
        assert score.score == 0.3  # Blog post score
    
    def test_calculate_review_score(self, scoring_engine, sample_provenance):
        """Test review score calculation."""
        score = scoring_engine._calculate_review_score(sample_provenance)
        
        assert score.score == 0.9  # Peer reviewed score
        assert "review_status" in score.explanation
        
        # Test different review statuses
        sample_provenance.review_status = ReviewStatus.SELF_PUBLISHED
        score = scoring_engine._calculate_review_score(sample_provenance)
        assert score.score == 0.4
    
    def test_calculate_currency_score(self, scoring_engine):
        """Test currency score calculation."""
        provenance = ProvenanceBlock()
        
        # Test with recent date
        provenance.publication_date = datetime.now() - timedelta(days=30)
        score = scoring_engine._calculate_currency_score(provenance)
        assert score.score >= 0.8  # Should be high for recent
        
        # Test with old date
        provenance.publication_date = datetime.now() - timedelta(days=365*5)
        score = scoring_engine._calculate_currency_score(provenance)
        assert score.score <= 0.5  # Should be lower for old
        
        # Test without date
        provenance.publication_date = None
        score = scoring_engine._calculate_currency_score(provenance)
        assert score.score == 0.5  # Default neutral score
        assert score.confidence < 0.5  # Low confidence without date
    
    def test_calculate_completeness_score(self, scoring_engine, sample_provenance):
        """Test completeness score calculation."""
        content_metadata = {
            "has_references": True,
            "has_citations": True,
            "word_count": 5000,
        }
        
        score = scoring_engine._calculate_completeness_score(
            sample_provenance, content_metadata
        )
        
        assert 0 <= score.score <= 1.0
        assert "completeness" in score.explanation.lower()
        assert "dimensions" in score.to_dict()
        
        # With all fields present and references, score should be high
        assert score.score >= 0.7
    
    def test_calculate_overall_score(self, scoring_engine):
        """Test overall score calculation."""
        trust_block = TrustBlock()
        
        # Create mock scores
        trust_block.authority_score = TrustScore(
            score=0.8, confidence=0.8, dimensions={}, explanation="", rule_applied=""
        )
        trust_block.document_type_score = TrustScore(
            score=0.9, confidence=0.9, dimensions={}, explanation="", rule_applied=""
        )
        trust_block.review_score = TrustScore(
            score=0.85, confidence=0.8, dimensions={}, explanation="", rule_applied=""
        )
        trust_block.currency_score = TrustScore(
            score=0.7, confidence=0.6, dimensions={}, explanation="", rule_applied=""
        )
        trust_block.completeness_score = TrustScore(
            score=0.8, confidence=0.7, dimensions={}, explanation="", rule_applied=""
        )
        
        overall = scoring_engine._calculate_overall_score(trust_block)
        
        assert isinstance(overall, TrustScore)
        assert 0 <= overall.score <= 1.0
        assert 0 <= overall.confidence <= 1.0
        assert "weighted average" in overall.explanation.lower()
        assert len(overall.dimensions) == 5  # All 5 dimensions
    
    def test_calculate_trust_scores_full(self, scoring_engine, sample_provenance):
        """Test complete trust score calculation."""
        content_metadata = {
            "has_references": True,
            "has_citations": True,
            "word_count": 3000,
        }
        
        trust_block = scoring_engine.calculate_trust_scores(
            sample_provenance, content_metadata
        )
        
        # Check all scores are present
        assert trust_block.overall_score is not None
        assert trust_block.authority_score is not None
        assert trust_block.document_type_score is not None
        assert trust_block.review_score is not None
        assert trust_block.currency_score is not None
        assert trust_block.completeness_score is not None
        
        # Check score ranges
        for score_name in ["overall_score", "authority_score", "document_type_score",
                          "review_score", "currency_score", "completeness_score"]:
            score = getattr(trust_block, score_name)
            if score:
                assert 0 <= score.score <= 1.0
                assert 0 <= score.confidence <= 1.0
                assert score.explanation is not None
    
    def test_custom_rules_configuration(self):
        """Test scoring with custom rules configuration."""
        custom_rules = {
            'weights': {
                'authority': 0.5,
                'document_type': 0.3,
                'review': 0.2,
                'currency': 0.0,
                'completeness': 0.0,
            },
            'document_type_scores': {
                'research_paper': 1.0,  # Max score for research papers
                'blog_post': 0.1,       # Very low for blog posts
            },
        }
        
        engine = TrustScoringEngine(rules_config=custom_rules)
        
        provenance = ProvenanceBlock(
            document_type=DocumentType.RESEARCH_PAPER,
            authors=["Test Author"],
        )
        
        content_metadata = {}
        trust_block = engine.calculate_trust_scores(provenance, content_metadata)
        
        # Document type score should be 1.0 with custom rules
        assert trust_block.document_type_score.score == 1.0