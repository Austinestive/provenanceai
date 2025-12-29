"""
Trust scoring engine.
Rule-based scoring with full explainability.
"""

from datetime import timezone
from typing import Any, Dict, List, Optional

from ..core.schema import (
    DocumentType,
    ProvenanceBlock,
    ReviewStatus,
    TrustBlock,
    TrustScore,
)


class TrustScoringEngine:
    """Rule-based trust scoring engine."""

    def __init__(self, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize scoring engine.

        Args:
            rules_config: Optional configuration for scoring rules.
                         If None, uses default rules.
        """
        self.rules = rules_config or self._get_default_rules()

    def calculate_trust_scores(
        self, provenance: ProvenanceBlock, content_metadata: Dict[str, Any]
    ) -> TrustBlock:
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
        trust_block.document_type_score = self._calculate_document_type_score(
            provenance
        )
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
                if any(
                    term in inst_lower
                    for term in [".gov", ".edu", "university", "college"]
                ):
                    inst_score = max(inst_score, 0.8)
                    rule_applied = "academic_gov_institution"
                elif any(
                    term in inst_lower for term in ["inc.", "corp", "ltd", "gmbh"]
                ):
                    inst_score = max(inst_score, 0.6)
                    rule_applied = "corporate_institution"
                else:
                    inst_score = max(inst_score, 0.4)

            dimensions["institution_authority"] = inst_score
            score = inst_score

        # Author count rule
        if len(provenance.authors) > 1:
            dimensions["multiple_authors"] = 0.7
            score = max(score, 0.7)
            rule_applied = "multiple_authors"

        # Known author patterns
        if provenance.authors:
            for author in provenance.authors:
                # Check for academic titles or degrees
                if any(title in author for title in ["Ph.D", "Dr.", "Professor"]):
                    dimensions["author_credentials"] = 0.8
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
            rule_applied=rule_applied,
        )

    def _calculate_document_type_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on document type."""
        default_scores = {
            DocumentType.RESEARCH_PAPER.value: 0.9,
            DocumentType.TECHNICAL_REPORT.value: 0.8,
            DocumentType.GOVERNMENT_DOCUMENT.value: 0.85,
            DocumentType.CONFERENCE_PAPER.value: 0.7,
            DocumentType.THESIS.value: 0.8,
            DocumentType.PATENT.value: 0.75,
            DocumentType.STANDARD.value: 0.85,
            DocumentType.NEWSPAPER_ARTICLE.value: 0.6,
            DocumentType.PREPRINT.value: 0.5,
            DocumentType.BLOG_POST.value: 0.3,
            DocumentType.WIKIPEDIA_ENTRY.value: 0.5,
            DocumentType.LEGAL_DOCUMENT.value: 0.7,
            DocumentType.UNKNOWN.value: 0.4,
        }

        configured = (self.rules or {}).get("document_type_scores") or {}
        doc_type = provenance.document_type or DocumentType.UNKNOWN
        score = configured.get(doc_type.value, default_scores.get(doc_type.value, 0.5))

        explanation = f"Document type '{doc_type.value}' has trust score {score}"

        return TrustScore(
            score=score,
            confidence=0.9,
            dimensions={"document_type": score},
            explanation=explanation,
            rule_applied="document_type_mapping",
        )

    def _calculate_review_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on review status."""
        default_scores = {
            ReviewStatus.PEER_REVIEWED.value: 0.9,
            ReviewStatus.EDITOR_REVIEWED.value: 0.7,
            ReviewStatus.SELF_PUBLISHED.value: 0.4,
            ReviewStatus.UNREVIEWED.value: 0.3,
        }

        configured = (self.rules or {}).get("review_scores") or {}
        review_status = provenance.review_status or ReviewStatus.UNREVIEWED
        score = configured.get(
            review_status.value, default_scores.get(review_status.value, 0.5)
        )

        explanation = f"review_status '{review_status.value}' contributes score {score}"

        return TrustScore(
            score=score,
            confidence=0.8,
            dimensions={"review_status": score},
            explanation=explanation,
            rule_applied="review_status_mapping",
        )

    def _calculate_currency_score(self, provenance: ProvenanceBlock) -> TrustScore:
        """Calculate score based on document currency (age)."""
        score = 0.5
        rule_applied = "default_neutral"

        if provenance.publication_date:
            from datetime import datetime

            current_year = datetime.now(timezone.utc).year
            publication_year = provenance.publication_date.year

            age = current_year - publication_year

            if age <= 1:
                score = 0.9
                rule_applied = "very_recent"
            elif age <= 3:
                score = 0.8
                rule_applied = "recent"
            elif age <= 5:
                score = 0.5
                rule_applied = "moderately_old"
            elif age <= 10:
                score = 0.4
                rule_applied = "old"
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
            dimensions={"currency": score},
            explanation=explanation,
            rule_applied=rule_applied,
        )

    def _calculate_completeness_score(
        self, provenance: ProvenanceBlock, content_metadata: Dict[str, Any]
    ) -> TrustScore:
        """Calculate score based on completeness of information."""
        completeness_factors = {}

        # Check for key provenance fields
        fields_to_check = [
            ("authors", bool(provenance.authors)),
            ("title", bool(provenance.title)),
            ("publication_date", bool(provenance.publication_date)),
            ("institutions", bool(provenance.institutions)),
        ]

        present_fields = sum(1 for _, present in fields_to_check if present)
        total_fields = len(fields_to_check)

        field_completeness = present_fields / total_fields
        completeness_factors["provenance_fields"] = field_completeness

        # Check content metadata
        if content_metadata.get("has_references"):
            completeness_factors["has_references"] = 0.8
        if content_metadata.get("has_citations"):
            completeness_factors["has_citations"] = 0.7

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
            rule_applied="completeness_analysis",
        )

    def _calculate_overall_score(self, trust_block: TrustBlock) -> TrustScore:
        """Calculate overall weighted trust score."""
        weights = (self.rules or {}).get("weights") or {
            "authority": 0.3,
            "document_type": 0.2,
            "review": 0.25,
            "currency": 0.15,
            "completeness": 0.1,
        }

        scores = {
            "authority": (
                trust_block.authority_score.score
                if trust_block.authority_score
                else 0.5
            ),
            "document_type": (
                trust_block.document_type_score.score
                if trust_block.document_type_score
                else 0.5
            ),
            "review": (
                trust_block.review_score.score if trust_block.review_score else 0.5
            ),
            "currency": (
                trust_block.currency_score.score if trust_block.currency_score else 0.5
            ),
            "completeness": (
                trust_block.completeness_score.score
                if trust_block.completeness_score
                else 0.5
            ),
        }

        # Weighted average
        weighted_sum = sum(scores[dim] * weight for dim, weight in weights.items())
        total_weight = sum(weights.values())
        overall_score = weighted_sum / total_weight

        # Confidence is average of confidences
        confidences = [
            (
                trust_block.authority_score.confidence
                if trust_block.authority_score
                else 0.5
            ),
            (
                trust_block.document_type_score.confidence
                if trust_block.document_type_score
                else 0.5
            ),
            trust_block.review_score.confidence if trust_block.review_score else 0.5,
            (
                trust_block.currency_score.confidence
                if trust_block.currency_score
                else 0.5
            ),
            (
                trust_block.completeness_score.confidence
                if trust_block.completeness_score
                else 0.5
            ),
        ]
        overall_confidence = sum(confidences) / len(confidences)

        explanation = "Overall trust score calculated as weighted average of: "
        explanation += ", ".join(
            f"{dim}({scores[dim]:.2f}*{weights[dim]})" for dim in weights.keys()
        )

        return TrustScore(
            score=overall_score,
            confidence=overall_confidence,
            dimensions=scores,
            explanation=explanation,
            rule_applied="weighted_average",
        )

    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default scoring rules."""
        return {
            "weights": {
                "authority": 0.3,
                "document_type": 0.2,
                "review": 0.25,
                "currency": 0.15,
                "completeness": 0.1,
            },
            "document_type_scores": {
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
            },
            "review_scores": {
                "peer_reviewed": 0.9,
                "editor_reviewed": 0.7,
                "self_published": 0.4,
                "unreviewed": 0.3,
            },
        }
