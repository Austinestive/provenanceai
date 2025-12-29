# File: src/provenanceai/utils/caching.py
"""
Simple caching utilities for performance.
"""

import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional


class DocumentCache:
    """Cache for document analysis results."""

    def __init__(self, cache_dir: Optional[Path] = None, max_size: int = 100) -> None:
        self.cache_dir = cache_dir or Path.home() / ".cache" / "provenanceai"
        self.max_size = max_size
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, file_path: Path) -> str:
        """Generate cache key from file hash and size."""
        file_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Just sample first and last 8KB for performance
            file_hash.update(f.read(8192))
            f.seek(-8192, 2)
            file_hash.update(f.read(8192))

        file_stat = file_path.stat()
        key_data = f"{file_hash.hexdigest()}_{file_stat.st_size}_{file_stat.st_mtime}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, file_path: Path) -> Optional[Any]:
        """Get cached result for file."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                # Corrupted cache file
                cache_file.unlink(missing_ok=True)

        return None

    def set(self, file_path: Path, result: Any) -> None:
        """Cache result for file."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        # Clean old cache files if we're at max size
        cache_files = list(self.cache_dir.glob("*.pkl"))
        if len(cache_files) >= self.max_size:
            # Remove oldest files
            cache_files.sort(key=lambda x: x.stat().st_mtime)
            for old_file in cache_files[: len(cache_files) - self.max_size + 1]:
                old_file.unlink(missing_ok=True)

        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
