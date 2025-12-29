# File: src/provenanceai/integration/rag_adapters.py
"""
RAG framework adapters for seamless integration.
"""

from typing import Any, Dict, List

from ..core.schema import AIUsagePermission, ProvenanceReport


class RAGMetadataAdapter:
    """Adapts ProvenanceReport to various RAG framework formats."""

    @staticmethod
    def for_langchain(report: ProvenanceReport) -> Dict[str, Any]:
        """Format metadata for LangChain documents."""
        metadata = report.to_dict()

        # Flatten key fields for easy filtering
        return {
            **metadata,
            "provenance_authors": report.provenance.authors,
            "provenance_institutions": report.provenance.institutions,
            "trust_score": (
                report.trust.overall_score.score if report.trust.overall_score else 0.0
            ),
            "document_type": (
                report.provenance.document_type.value
                if report.provenance.document_type
                else None
            ),
            "ai_allowed_actions": [
                action.value for action in report.ai_use.allowed_actions
            ],
        }

    @staticmethod
    def for_llamaindex(report: ProvenanceReport) -> Dict[str, Any]:
        """Format metadata for LlamaIndex nodes."""
        metadata = report.to_dict()

        # LlamaIndex specific formatting
        return {
            "extra_info": {
                "provenance": metadata,
                "trust_summary": {
                    "score": (
                        report.trust.overall_score.score
                        if report.trust.overall_score
                        else 0.0
                    ),
                    "explanation": (
                        report.trust.overall_score.explanation
                        if report.trust.overall_score
                        else ""
                    ),
                },
            }
        }

    @staticmethod
    def for_vectordb(report: ProvenanceReport) -> Dict[str, Any]:
        """
        Format for vector databases (Chroma, Pinecone, Weaviate).
        Optimized for filtering and similarity search.
        """
        return {
            # Searchable fields
            "authors": report.provenance.authors,
            "institutions": report.provenance.institutions,
            "document_type": (
                report.provenance.document_type.value
                if report.provenance.document_type
                else "unknown"
            ),
            "publication_year": (
                report.provenance.publication_date.year
                if report.provenance.publication_date
                else None
            ),
            "language": report.content.language,
            # Trust filtering
            "trust_score": (
                report.trust.overall_score.score if report.trust.overall_score else 0.0
            ),
            "trust_category": _categorize_trust_score(
                report.trust.overall_score.score if report.trust.overall_score else 0.0
            ),
            # AI usage flags
            "ai_can_summarize": AIUsagePermission.ALLOWED
            in report.ai_use.allowed_actions,
            "ai_can_train": AIUsagePermission.NO_TRAINING
            not in report.ai_use.prohibited_actions,
            "attribution_required": report.ai_use.attribution_required,
            # Full provenance (JSON string for databases that support it)
            "provenance_full": report.to_json(),
        }


def _categorize_trust_score(score: float) -> str:
    """Categorize trust score for easy filtering."""
    if score >= 0.8:
        return "high"
    elif score >= 0.6:
        return "medium"
    elif score >= 0.4:
        return "low"
    else:
        return "untrusted"
