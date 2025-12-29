"""
Data validation utilities.
"""

from pathlib import Path
from typing import Union

from .exceptions import DocumentLoadError, ValidationError


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """Validate that file exists and is readable."""
    path = Path(file_path)

    if not path.exists():
        raise DocumentLoadError(f"File does not exist: {path}")

    if not path.is_file():
        raise DocumentLoadError(f"Path is not a file: {path}")

    if path.stat().st_size == 0:
        raise DocumentLoadError(f"File is empty: {path}")

    # Check file size limit (100MB)
    if path.stat().st_size > 100 * 1024 * 1024:
        raise DocumentLoadError(f"File too large (max 100MB): {path}")

    return path


def validate_config_dict(config: dict) -> None:
    """Validate configuration dictionary."""
    required_sections = ["trust_scoring", "policy"]

    for section in required_sections:
        if section not in config:
            raise ValidationError(f"Missing configuration section: {section}")

    # Validate trust scoring weights sum to ~1.0
    trust_scoring = config.get("trust_scoring", {})
    if "weights" in trust_scoring:
        weights = trust_scoring["weights"]
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point differences
            raise ValidationError(
                f"Trust scoring weights must sum to 1.0, got {total:.2f}"
            )
