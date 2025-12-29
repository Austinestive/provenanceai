"""
ProvenanceAI - Knowledge Provenance & Trust Infrastructure for AI
"""

__version__: str = "0.1.0"
__author__: str = "ProvenanceAI Team"
__description__: str = (
    "A standard, explainable way for AI systems to understand provenance and trustworthiness of knowledge sources"
)

from .api import ProvenanceReport, analyze
from .core.schema import (
    AIUsagePermission,
    DocumentType,
    LicenseType,
    ProvenanceReport,
    ReviewStatus,
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
