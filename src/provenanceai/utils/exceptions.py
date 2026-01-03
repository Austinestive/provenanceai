# File: src/provenanceai/utils/exceptions.py
"""
Custom exceptions for ProvenanceAI.
"""


class ProvenanceAIError(Exception):
    """Base exception for ProvenanceAI."""

    pass


class DocumentLoadError(ProvenanceAIError):
    """Failed to load document."""

    pass


class InferenceError(ProvenanceAIError):
    """Failed to infer provenance."""

    pass


class ConfigurationError(ProvenanceAIError):
    """Invalid configuration."""

    pass


class ValidationError(ProvenanceAIError):
    """Data validation failed."""

    pass
