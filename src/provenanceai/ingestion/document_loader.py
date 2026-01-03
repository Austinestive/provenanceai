"""
Document ingestion module.
Supports multiple file formats with consistent metadata extraction.
"""

import hashlib
import mimetypes
import sys
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, Union

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None


class DocumentLoader:
    """Base document loader with common functionality."""

    SUPPORTED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".htm": "text/html",
    }

    def __init__(self) -> None:
        self.mime_types = mimetypes.MimeTypes()

    def can_load(self, file_path: Union[str, Path]) -> bool:
        """Check if this loader can handle the given file."""
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def calculate_file_hash(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA-256 hash of file."""
        path = Path(file_path)
        sha256_hash = hashlib.sha256()

        with open(path, "rb") as f:
            # Read file in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def extract_basic_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract basic file metadata."""
        path = Path(file_path)

        return {
            "filename": path.name,
            "file_extension": path.suffix.lower(),
            "file_size_bytes": path.stat().st_size,
            "created_timestamp": path.stat().st_ctime,
            "modified_timestamp": path.stat().st_mtime,
            "absolute_path": str(path.absolute()),
        }

    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load document and extract both content and metadata.

        Returns:
            Dictionary with 'content' and 'metadata' keys
        """
        raise NotImplementedError("Subclasses must implement load_document")

    def get_mime_type(self, file_path: Union[str, Path]) -> str:
        """Get MIME type of file."""
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(str(path))

        if mime_type:
            return mime_type

        # Fallback to our mapping
        return self.SUPPORTED_EXTENSIONS.get(
            path.suffix.lower(), "application/octet-stream"
        )


class TextDocumentLoader(DocumentLoader):
    """Loader for plain text documents."""

    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        path = Path(file_path)

        if path.suffix.lower() not in {".txt", ".md", ".html", ".htm"}:
            raise ValueError(
                f"Unsupported file type for TextDocumentLoader: {path.suffix.lower()}"
            )

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        metadata = self.extract_basic_metadata(path)
        metadata.update(
            {
                "mime_type": self.get_mime_type(path),
                "file_hash": self.calculate_file_hash(path),
                "character_count": len(content),
                "line_count": content.count("\n") + 1,
            }
        )

        return {
            "content": content,
            "metadata": metadata,
        }


class PDFDocumentLoader(DocumentLoader):
    """Loader for PDF documents."""

    def __init__(self) -> None:
        super().__init__()
        # Lazy import to avoid dependency if not used
        self._pymupdf: Optional[Any] = None

    def _ensure_pymupdf(self) -> None:
        """Ensure PyMuPDF is available."""
        if self._pymupdf is None:
            # Tests may patch sys.modules['fitz'] = None to simulate missing dependency.
            if "fitz" in sys.modules and sys.modules["fitz"] is None:
                raise ImportError(
                    "PyMuPDF (fitz) is required for PDF loading. "
                    "Install with: pip install pymupdf"
                )

            # Prefer the module-level 'fitz' symbol so tests can patch it reliably.
            if fitz is None:
                raise ImportError(
                    "PyMuPDF (fitz) is required for PDF loading. "
                    "Install with: pip install pymupdf"
                )
            self._pymupdf = fitz

    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        self._ensure_pymupdf()
        assert self._pymupdf is not None  # Type narrowing for mypy
        path = Path(file_path)

        doc = self._pymupdf.open(str(path))

        # Extract text from all pages
        content_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            content_parts.append(page.get_text())

        content = "\n\n".join(content_parts)

        # Extract metadata from PDF info
        pdf_metadata = doc.metadata

        metadata = self.extract_basic_metadata(path)
        try:
            file_hash = self.calculate_file_hash(path)
        except OSError:
            file_hash = None
        metadata.update(
            {
                "mime_type": "application/pdf",
                "file_hash": file_hash,
                "pdf_metadata": pdf_metadata,
                "page_count": len(doc),
                "author": pdf_metadata.get("author"),
                "title": pdf_metadata.get("title"),
                "subject": pdf_metadata.get("subject"),
                "keywords": pdf_metadata.get("keywords"),
                "creator": pdf_metadata.get("creator"),
                "producer": pdf_metadata.get("producer"),
                "creation_date": pdf_metadata.get("creationDate"),
                "modification_date": pdf_metadata.get("modDate"),
            }
        )

        doc.close()

        return {
            "content": content,
            "metadata": metadata,
        }


class DOCXDocumentLoader(DocumentLoader):
    """Loader for DOCX documents."""

    def __init__(self) -> None:
        super().__init__()
        self._python_docx: Optional[Any] = None

    def _ensure_python_docx(self) -> None:
        """Ensure python-docx is available."""
        if self._python_docx is None:
            try:
                import docx

                self._python_docx = docx
            except ImportError:
                raise ImportError(
                    "python-docx is required for DOCX loading. "
                    "Install with: pip install python-docx"
                )

    def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        self._ensure_python_docx()
        assert self._python_docx is not None  # Type narrowing for mypy
        path = Path(file_path)

        doc = self._python_docx.Document(str(path))

        # Extract text from all paragraphs
        content_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content_parts.append(paragraph.text)

        content = "\n\n".join(content_parts)

        # Extract core properties
        core_props = doc.core_properties

        metadata = self.extract_basic_metadata(path)
        metadata.update(
            {
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "file_hash": self.calculate_file_hash(path),
                "author": core_props.author,
                "title": core_props.title,
                "subject": core_props.subject,
                "keywords": core_props.keywords,
                "last_modified_by": core_props.last_modified_by,
                "created": core_props.created,
                "modified": core_props.modified,
                "category": core_props.category,
                "comments": core_props.comments,
                "paragraph_count": len(content_parts),
            }
        )

        return {
            "content": content,
            "metadata": metadata,
        }


class DocumentLoaderFactory:
    """Factory for creating appropriate document loaders."""

    LOADERS = {
        ".pdf": "PDFDocumentLoader",
        ".docx": "DOCXDocumentLoader",
        ".txt": "TextDocumentLoader",
        ".md": "TextDocumentLoader",
        ".html": "TextDocumentLoader",
        ".htm": "TextDocumentLoader",
    }

    @classmethod
    def get_loader(cls, file_path: Union[str, Path]) -> "DocumentLoader":
        """Get appropriate loader for file type."""
        path = Path(file_path)
        extension = path.suffix.lower()

        loader_class_name = cls.LOADERS.get(extension)
        if loader_class_name is None:
            raise ValueError(f"Unsupported file type: {extension}")

        loader_class = globals().get(loader_class_name)
        if loader_class is None:
            raise RuntimeError(f"Loader class not found: {loader_class_name}")

        return loader_class()  # type: ignore[no-any-return]

    @classmethod
    def load_document(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load document using appropriate loader."""
        loader = cls.get_loader(file_path)
        return loader.load_document(file_path)
