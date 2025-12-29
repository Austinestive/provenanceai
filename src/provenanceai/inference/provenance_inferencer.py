"""
Provenance inference module.
Uses heuristics and NER to infer provenance information.
"""

import re
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..core.schema import (
    DocumentType,
    ExplainabilityBlock,
    ProvenanceBlock,
    ReviewStatus,
)


class ProvenanceInferencer:
    """Infers provenance information from document content and metadata."""

    # Patterns for inference
    EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    URL_PATTERN = r"https?://[^\s]+"
    DOI_PATTERN = r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"
    ARXIV_PATTERN = r"arXiv:\d{4}\.\d{4,5}(v\d+)?"
    DATE_PATTERNS = [
        r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
        r"\d{4}",  # Just year
    ]

    def __init__(self) -> None:
        self.inference_sources: List[str] = []
        self.confidence_scores: Dict[str, float] = {}
        self.warnings: List[str] = []

    def infer_from_metadata(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[ProvenanceBlock, ExplainabilityBlock]:
        """
        Infer provenance information from document content and metadata.

        Returns:
            Tuple of (ProvenanceBlock, ExplainabilityBlock)
        """
        provenance = ProvenanceBlock()
        explainability = ExplainabilityBlock()

        # Document type inference
        doc_type, doc_type_source = self._infer_document_type(content, metadata)
        provenance.document_type = doc_type
        self._record_inference("document_type", doc_type_source)

        # Author inference
        authors, author_source = self._infer_authors(content, metadata)
        provenance.authors = authors
        self._record_inference("authors", author_source)

        # Institution inference
        institutions, inst_source = self._infer_institutions(content, metadata)
        provenance.institutions = institutions
        self._record_inference("institutions", inst_source)

        # Date inference
        pub_date, date_source = self._infer_publication_date(content, metadata)
        provenance.publication_date = pub_date
        self._record_inference("publication_date", date_source)

        # Title inference
        title, title_source = self._infer_title(content, metadata)
        provenance.title = title
        self._record_inference("title", title_source)

        # Review status inference
        review_status, review_source = self._infer_review_status(
            content, metadata, doc_type
        )
        provenance.review_status = review_status
        self._record_inference("review_status", review_source)

        # Citation inference
        citation, citation_source = self._infer_citation(provenance)
        provenance.citation = citation
        self._record_inference("citation", citation_source)

        # Set retrieved date to now
        provenance.retrieved_date = datetime.now(timezone.utc)

        # Update explainability block
        explainability.inference_sources = self.inference_sources
        explainability.confidence_scores = self.confidence_scores.copy()
        explainability.warnings = self.warnings.copy()

        return provenance, explainability

    def _infer_document_type(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[Optional[DocumentType], str]:
        """Infer document type from content and metadata."""
        text_lower = content.lower()
        # Check for arXiv patterns
        if re.search(self.ARXIV_PATTERN, content, re.IGNORECASE):
            return DocumentType.PREPRINT, "arxiv_id_detected"

        # Check for DOI
        if re.search(self.DOI_PATTERN, content, re.IGNORECASE):
            # Check if it's a thesis by common patterns
            if any(word in text_lower for word in ["thesis", "dissertation", "phd"]):
                return DocumentType.THESIS, "doi_with_thesis_keywords"
            return DocumentType.RESEARCH_PAPER, "doi_detected"

        # Check for legal document patterns
        legal_terms = ["case no", "v.", "plaintiff", "defendant", "court", "legal"]
        if any(term in text_lower for term in legal_terms):
            return DocumentType.LEGAL_DOCUMENT, "legal_terminology"

        # Check metadata for clues
        if "pdf_metadata" in metadata:
            pdf_meta = metadata["pdf_metadata"]
            if pdf_meta.get("keywords", ""):
                keywords = pdf_meta["keywords"].lower()
                if "patent" in keywords:
                    return DocumentType.PATENT, "pdf_keywords"

        # Check file name for clues
        filename = metadata.get("filename", "").lower()
        if "report" in filename:
            return DocumentType.TECHNICAL_REPORT, "filename_pattern"
        elif "patent" in filename:
            return DocumentType.PATENT, "filename_pattern"

        return DocumentType.UNKNOWN, "no_strong_indicators"

    def _infer_authors(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[List[str], str]:
        """Infer authors from content and metadata."""
        authors = []
        source = "metadata_extraction"

        # First, check metadata
        if metadata.get("author"):
            authors.append(metadata["author"])
            source = "metadata_author_field"

        # Check PDF metadata
        if "pdf_metadata" in metadata and metadata["pdf_metadata"].get("author"):
            pdf_author = metadata["pdf_metadata"]["author"]
            if pdf_author not in authors:
                authors.append(pdf_author)
                source = "pdf_metadata"

        # Try to extract from first few lines of content
        if not authors:
            first_lines = content[:1000].split("\n")
            for line in first_lines[:10]:  # Check first 10 lines
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                line_lower = line_stripped.lower()
                # Avoid substring matches like "without authors"; look for labels.
                if re.match(r"^\s*(authors?|by)\b", line_lower) or re.search(
                    r"\bwritten by\b", line_lower
                ):
                    authors.append(line_stripped)
                    source = "content_analysis"
                    break

        return authors, source

    def _infer_institutions(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[List[str], str]:
        """Infer institutions from content and metadata."""
        institutions = []
        source = "no_institutions_found"

        # Common institution patterns
        institution_keywords = [
            "university",
            "college",
            "institute",
            "laboratory",
            "lab",
            "center for",
            "department of",
            "school of",
            "corporation",
            "inc.",
            "ltd.",
            "gmbh",
            "government",
            "ministry",
            "agency",
        ]

        # Check first few paragraphs
        paragraphs = content.split("\n\n")[:5]
        for para in paragraphs:
            para_lower = para.lower()
            for keyword in institution_keywords:
                if keyword in para_lower:
                    # Extract the institution name (simplified)
                    institutions.append(para.strip()[:100])  # First 100 chars
                    source = "keyword_matching"
                    break

        # Check email domains for institutions
        email_matches = re.findall(self.EMAIL_PATTERN, content)
        for email in email_matches[:5]:  # Limit to first 5 emails
            domain = email.split("@")[1]
            # Check if domain looks like an institution
            if any(edu in domain for edu in [".edu", ".ac.", ".gov"]):
                institutions.append(domain)
                source = "email_domain_analysis"

        return list(set(institutions)), source

    def _infer_publication_date(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[Optional[datetime], str]:
        """Infer publication date from content and metadata."""
        source = "no_date_found"

        # Check metadata first
        date_fields = ["created", "modified", "creation_date", "modification_date"]
        for field in date_fields:
            if field in metadata and metadata[field]:
                try:
                    # Parse date - implementation depends on format
                    # This is a simplified version
                    return (
                        datetime.fromisoformat(str(metadata[field])[:10]),
                        f"metadata_{field}",
                    )
                except (ValueError, TypeError):
                    continue

        # Search for date patterns in content
        first_1000_chars = content[:1000]
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, first_1000_chars)
            if matches:
                try:
                    date_str = matches[0]
                    if len(date_str) == 4:  # Just year
                        return datetime(int(date_str), 1, 1), "year_pattern_in_content"
                    # For other patterns, would need proper parsing
                except ValueError:
                    continue

        return None, source

    def _infer_title(
        self, content: str, metadata: Dict[str, Any]
    ) -> Tuple[Optional[str], str]:
        """Infer title from content and metadata."""
        source = "no_title_found"

        # Check metadata first
        if metadata.get("title"):
            return metadata["title"], "metadata_title_field"

        if "pdf_metadata" in metadata and metadata["pdf_metadata"].get("title"):
            return metadata["pdf_metadata"]["title"], "pdf_metadata"

        # Try to extract from first line
        first_line = content.split("\n")[0].strip()
        if len(first_line) < 200 and len(first_line) > 10:  # Reasonable title length
            return first_line, "first_line_extraction"

        return None, source

    def _infer_review_status(
        self, content: str, metadata: Dict[str, Any], doc_type: Optional[DocumentType]
    ) -> Tuple[Optional[ReviewStatus], str]:
        """Infer review status from content, metadata, and document type."""

        if doc_type == DocumentType.PREPRINT:
            return ReviewStatus.UNREVIEWED, "preprint_implication"

        text_lower = content.lower()

        # Check for peer review mentions
        if any(
            term in text_lower
            for term in [
                "peer-reviewed",
                "reviewed by",
                "refereed",
                "this paper was reviewed",
            ]
        ):
            return ReviewStatus.PEER_REVIEWED, "explicit_peer_review_mention"

        # Check for journal indicators
        journal_indicators = ["journal of", "vol.", "no.", "pp.", "doi.org"]
        if any(indicator in text_lower for indicator in journal_indicators):
            return ReviewStatus.PEER_REVIEWED, "journal_formatting"

        # Check for blog indicators
        blog_indicators = ["posted on", "blog", "medium.com"]
        if any(indicator in text_lower for indicator in blog_indicators):
            return ReviewStatus.SELF_PUBLISHED, "blog_formatting"

        return ReviewStatus.UNREVIEWED, "default_unreviewed"

    def _infer_citation(self, provenance: ProvenanceBlock) -> Tuple[Optional[str], str]:
        """Generate citation from provenance information."""
        if not provenance.authors or not provenance.title:
            return None, "insufficient_data"

        # Simple citation format: Authors (Year) Title
        authors_str = "; ".join(provenance.authors[:3])  # Limit to first 3 authors
        year = (
            provenance.publication_date.year if provenance.publication_date else "n.d."
        )

        citation = f"{authors_str} ({year}). {provenance.title}"

        if provenance.institutions:
            citation += f". {provenance.institutions[0]}"

        return citation, "generated_from_provenance"

    def _record_inference(
        self, field: str, source: str, confidence: float = 0.5
    ) -> None:
        """Record inference source and confidence."""
        """Record inference source and confidence."""
        self.inference_sources.append(f"{field}: {source}")
        self.confidence_scores[field] = confidence
