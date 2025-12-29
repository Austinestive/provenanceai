"""
AI Usage Policy Engine.
Determines what AI may do with content based on provenance and license.
"""

from typing import Any, Dict, List, Optional

from ..core.schema import (
    AIUsagePermission,
    AIUseBlock,
    DocumentType,
    LicenseType,
    ProvenanceBlock,
    TrustBlock,
)


class AIPolicyEngine:
    """Determines AI usage policies from provenance and trust information."""

    def __init__(self, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize policy engine.

        Args:
            rules_config: Optional configuration for policy rules.
        """
        self.rules = rules_config or self._get_default_rules()

    def determine_policy(
        self, provenance: ProvenanceBlock, trust: TrustBlock
    ) -> AIUseBlock:
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

    def _infer_license(
        self, provenance: ProvenanceBlock, trust: TrustBlock
    ) -> LicenseType:
        """Infer license from provenance and trust."""
        doc_type = provenance.document_type

        # Government documents are typically public domain
        if doc_type == DocumentType.GOVERNMENT_DOCUMENT:
            return LicenseType.PUBLIC_DOMAIN

        # Academic papers often have specific licenses
        if doc_type in [
            DocumentType.RESEARCH_PAPER,
            DocumentType.CONFERENCE_PAPER,
            DocumentType.THESIS,
            DocumentType.PREPRINT,
        ]:

            # Check for arXiv (typically CC-BY)
            if provenance.citation and "arXiv" in provenance.citation:
                return LicenseType.CC_BY

            # Many academic papers are copyrighted but allow certain uses
            return LicenseType.COPYRIGHTED

        # Technical reports and standards often have specific terms
        if doc_type in [DocumentType.TECHNICAL_REPORT, DocumentType.STANDARD]:
            return LicenseType.COPYRIGHTED

        # Default to unknown
        return LicenseType.UNKNOWN

    def _set_permissions(
        self, ai_use: AIUseBlock, provenance: ProvenanceBlock, trust: TrustBlock
    ) -> None:
        """Set allowed and prohibited actions."""
        # Default permissions for high-trust documents
        if trust.overall_score and trust.overall_score.score >= 0.7:
            ai_use.allowed_actions.extend(
                [
                    AIUsagePermission.ALLOWED,
                    AIUsagePermission.ATTRIBUTION_REQUIRED,
                ]
            )
            ai_use.commercial_use_allowed = True
        else:
            # More restrictive for low-trust documents
            ai_use.allowed_actions.append(AIUsagePermission.ALLOWED)
            ai_use.commercial_use_allowed = False
            ai_use.prohibited_actions.append(AIUsagePermission.NON_COMMERCIAL_ONLY)

        # License-specific restrictions
        if ai_use.license == LicenseType.CC_BY_NC:
            ai_use.commercial_use_allowed = False
            ai_use.prohibited_actions.append(AIUsagePermission.NON_COMMERCIAL_ONLY)
            ai_use.allowed_actions.append(AIUsagePermission.ATTRIBUTION_REQUIRED)

        elif ai_use.license == LicenseType.COPYRIGHTED:
            # Be conservative with copyrighted material
            ai_use.allowed_actions.extend(
                [
                    AIUsagePermission.ATTRIBUTION_REQUIRED,
                    AIUsagePermission.NO_TRAINING,
                ]
            )
            ai_use.prohibited_actions.extend(
                [
                    AIUsagePermission.NO_TRAINING,
                    AIUsagePermission.NO_QUOTING,
                ]
            )

        elif ai_use.license == LicenseType.PUBLIC_DOMAIN:
            # Most permissive
            ai_use.allowed_actions.extend(
                [
                    AIUsagePermission.ALLOWED,
                    AIUsagePermission.ATTRIBUTION_REQUIRED,
                ]
            )
            ai_use.commercial_use_allowed = True

    def _set_attribution(
        self, ai_use: AIUseBlock, provenance: ProvenanceBlock, trust: TrustBlock
    ) -> None:
        """Set attribution requirements."""
        ai_use.attribution_required = True  # Default to requiring attribution

        if provenance.citation:
            ai_use.attribution_text = provenance.citation
        elif provenance.title and provenance.authors:
            authors = "; ".join(provenance.authors[:3])
            year = (
                provenance.publication_date.year
                if provenance.publication_date
                else "n.d."
            )
            ai_use.attribution_text = f"{authors} ({year}). {provenance.title}"

        # Public domain might not require attribution
        if ai_use.license == LicenseType.PUBLIC_DOMAIN:
            ai_use.attribution_required = False
            ai_use.attribution_text = None

    def _set_conditions(
        self, ai_use: AIUseBlock, provenance: ProvenanceBlock, trust: TrustBlock
    ) -> None:
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
        if provenance.review_status and provenance.review_status.value == "preprint":
            conditions.append("Preprint - not peer reviewed")

        ai_use.conditions = conditions

    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default policy rules."""
        return {
            "license_mappings": {
                "government_document": "public_domain",
                "arxiv_preprint": "CC_BY",
                "academic_paper": "copyrighted",
            },
            "trust_thresholds": {
                "high_trust": 0.7,
                "medium_trust": 0.5,
                "low_trust": 0.3,
            },
            "default_permissions": {
                "high_trust": ["allowed", "attribution_required"],
                "medium_trust": ["allowed"],
                "low_trust": ["allowed", "non_commercial_only"],
            },
        }
