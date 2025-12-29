# File: src/provenanceai/config/__init__.py
"""
Configuration management for ProvenanceAI.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class TrustScoringConfig:
    """Trust scoring configuration."""

    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "authority": 0.3,
            "document_type": 0.2,
            "review": 0.25,
            "currency": 0.15,
            "completeness": 0.1,
        }
    )

    document_type_scores: Dict[str, float] = field(
        default_factory=lambda: {
            "research_paper": 0.9,
            "government_document": 0.85,
            "technical_report": 0.8,
            "thesis": 0.8,
            "conference_paper": 0.7,
            "patent": 0.75,
            "newspaper_article": 0.6,
            "preprint": 0.5,
            "blog_post": 0.3,
            "unknown": 0.4,
        }
    )

    review_scores: Dict[str, float] = field(
        default_factory=lambda: {
            "peer_reviewed": 0.9,
            "editor_reviewed": 0.7,
            "self_published": 0.4,
            "unreviewed": 0.3,
        }
    )


@dataclass
class PolicyConfig:
    """AI policy configuration."""

    license_mappings: Dict[str, str] = field(
        default_factory=lambda: {
            "government_document": "public_domain",
            "arxiv_preprint": "CC_BY",
            "academic_paper": "copyrighted",
        }
    )

    trust_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "high_trust": 0.7,
            "medium_trust": 0.5,
            "low_trust": 0.3,
        }
    )


@dataclass
class ProvenanceAIConfig:
    """Main configuration container."""

    trust_scoring: TrustScoringConfig = field(default_factory=TrustScoringConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "ProvenanceAIConfig":
        """Load configuration from YAML file."""
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        return cls(
            trust_scoring=TrustScoringConfig(**config_dict.get("trust_scoring", {})),
            policy=PolicyConfig(**config_dict.get("policy", {})),
        )

    @classmethod
    def from_json(cls, config_path: Path) -> "ProvenanceAIConfig":
        """Load configuration from JSON file."""
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)

        return cls(
            trust_scoring=TrustScoringConfig(**config_dict.get("trust_scoring", {})),
            policy=PolicyConfig(**config_dict.get("policy", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "trust_scoring": asdict(self.trust_scoring),
            "policy": asdict(self.policy),
        }


# Default configuration
DEFAULT_CONFIG = ProvenanceAIConfig()
