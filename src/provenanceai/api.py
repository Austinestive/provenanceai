"""
Main public API for ProvenanceAI.
Provides the unified analyze() function.
"""

import json
from pathlib import Path
from typing import Optional, Union

from .core.schema import ContentBlock, IdentityBlock, ProvenanceReport, TechnicalBlock
from .inference.provenance_inferencer import ProvenanceInferencer
from .ingestion.document_loader import DocumentLoaderFactory
from .policy.ai_policy_engine import AIPolicyEngine
from .trust.scoring_engine import TrustScoringEngine


def analyze(
    file_path: Union[str, Path], config_path: Optional[Union[str, Path]] = None
) -> ProvenanceReport:
    """
    Main entry point for ProvenanceAI analysis.

    Args:
        file_path: Path to document to analyze
        config_path: Optional path to configuration file

    Returns:
        Complete ProvenanceReport with all analysis results

    Example:
        >>> from provenanceai import analyze
        >>> report = analyze("document.pdf")
        >>> print(report.to_json())
    """
    # 1. Load and validate input
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    # 2. Load configuration (simplified - would load from file)
    config = _load_config(config_path) if config_path else {}

    # 3. Document ingestion
    loader_result = DocumentLoaderFactory.load_document(path)
    content = loader_result["content"]
    metadata = loader_result["metadata"]

    if not str(content).strip():
        raise ValueError(f"Document is empty: {path}")

    # 4. Initialize components
    inferencer = ProvenanceInferencer()
    scoring_engine = TrustScoringEngine(config.get("trust_rules"))
    policy_engine = AIPolicyEngine(config.get("policy_rules"))

    # 5. Perform provenance inference
    provenance, explainability = inferencer.infer_from_metadata(content, metadata)

    # 6. Calculate trust scores
    content_metadata = {
        "has_references": _check_for_references(content),
        "has_citations": _check_for_citations(content),
        "word_count": len(content.split()),
    }
    trust = scoring_engine.calculate_trust_scores(provenance, content_metadata)

    # 7. Determine AI usage policy
    ai_use = policy_engine.determine_policy(provenance, trust)

    # 8. Build final report
    report = ProvenanceReport(
        identity=_build_identity_block(path, metadata),
        provenance=provenance,
        content=_build_content_block(content, metadata),
        trust=trust,
        ai_use=ai_use,
        explainability=explainability,
        technical=_build_technical_block(metadata),
    )

    return report


def _load_config(config_path: Union[str, Path]) -> dict:
    """Load configuration from file."""
    path = Path(config_path)
    if not path.exists():
        return {}

    suffix = path.suffix.lower()
    if suffix not in {".json", ".yaml", ".yml"}:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    with open(path, "r", encoding="utf-8") as f:
        if suffix == ".json":
            return json.load(f)  # type: ignore[no-any-return]
        import yaml
        return yaml.safe_load(f)  # type: ignore[no-any-return]


def _check_for_references(content: str) -> bool:
    """Check if document has references section."""
    import re

    # Treat as a section header, not just the word appearing in a sentence.
    return (
        re.search(
            r"(?mi)^\s*(references|bibliography|works\s+cited|sources)\s*:?\s*$",
            content,
        )
        is not None
    )


def _check_for_citations(content: str) -> bool:
    """Check if document has citations."""
    # Simple pattern matching for citations
    import re

    citation_patterns = [
        r"\([A-Za-z]+,\s*\d{4}\)",  # (Author, 2014)
        r"\[[\d,\s]+\]",  # [1, 2, 3]
        r"\d{4}[a-z]?",  # 2014a (common in citations)
    ]

    for pattern in citation_patterns:
        if re.search(pattern, content):
            return True
    return False


def _build_identity_block(path: Path, metadata: dict) -> IdentityBlock:
    """Build identity block from file metadata."""
    from .core.schema import IdentityBlock
    from .ingestion.document_loader import DocumentLoaderFactory

    # Get a loader to calculate hash
    loader = DocumentLoaderFactory.get_loader(path)

    file_hash = metadata.get("file_hash")
    if file_hash is None:
        try:
            file_hash = loader.calculate_file_hash(path)
        except (OSError, PermissionError):
            file_hash = None

    return IdentityBlock(
        original_filename=path.name,
        file_size_bytes=metadata.get("file_size_bytes"),
        mime_type=metadata.get("mime_type"),
        file_hash=file_hash,
    )


def _build_content_block(content: str, metadata: dict) -> ContentBlock:
    """Build content analysis block."""
    from langdetect import detect

    from .core.schema import ContentBlock

    try:
        language = detect(content[:1000])  # Sample first 1000 chars
    except Exception:
        language = "unknown"

    return ContentBlock(
        language=language,
        word_count=len(content.split()),
        page_count=metadata.get("page_count") or metadata.get("paragraph_count"),
        keywords=(
            metadata.get("keywords", "").split(";") if metadata.get("keywords") else []
        ),
        has_references=_check_for_references(content),
        has_citations=_check_for_citations(content),
    )


def _build_technical_block(metadata: dict) -> TechnicalBlock:
    """Build technical metadata block."""
    from .core.schema import TechnicalBlock

    return TechnicalBlock(
        processor_version="0.1.0",
        raw_metadata={
            k: v for k, v in metadata.items() if not isinstance(v, (bytes, type(None)))
        },
    )
