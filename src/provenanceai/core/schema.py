"""
Core schema definitions for ProvenanceAI.
Python dataclasses with JSON serialization support.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
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
                if hasattr(value, "to_dict"):
                    result[key] = value.to_dict()
                elif isinstance(value, dict):
                    result[key] = {
                        k: v.to_dict() if hasattr(v, "to_dict") else v
                        for k, v in value.items()
                    }
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

    inference_sources: List[str] = field(
        default_factory=list
    )  # How each field was determined
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    assumptions_made: List[str] = field(default_factory=list)
    metadata_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return (
            "ExplainabilityBlock(explanation: inference_sources="
            f"{len(self.inference_sources)}, confidence_scores={len(self.confidence_scores)}, "
            f"warnings={len(self.warnings)})"
        )


@dataclass
class TechnicalBlock:
    """Technical metadata block."""

    schema_version: str = "1.0.0"
    processing_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)  # UPDATED
    )
    processor_version: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert datetime to ISO format
        if isinstance(result.get("processing_timestamp"), datetime):
            # Ensure timezone aware ISO format
            dt = result["processing_timestamp"]
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            result["processing_timestamp"] = dt.isoformat()
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
            "identity": self.identity.to_dict(),
            "provenance": self.provenance.to_dict(),
            "content": self.content.to_dict(),
            "trust": self.trust.to_dict(),
            "ai_use": self.ai_use.to_dict(),
            "explainability": self.explainability.to_dict(),
            "technical": self.technical.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize the report to JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceReport":
        """Create a report from a dictionary."""
        # This is a simplified version - would need full implementation
        return cls()
