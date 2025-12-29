# File: tests/unit/test_document_ingestion.py
"""
Unit tests for document ingestion module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import tempfile

from provenanceai.ingestion.document_loader import (
    DocumentLoader,
    TextDocumentLoader,
    PDFDocumentLoader,
    DOCXDocumentLoader,
    DocumentLoaderFactory,
)


class TestDocumentLoader:
    """Test base document loader functionality."""
    
    def test_can_load_supported_formats(self):
        """Test can_load method for supported formats."""
        loader = DocumentLoader()
        
        assert loader.can_load("document.pdf") is True
        assert loader.can_load("document.docx") is True
        assert loader.can_load("document.txt") is True
        assert loader.can_load("document.md") is True
        assert loader.can_load("document.html") is True
    
    def test_can_load_unsupported_formats(self):
        """Test can_load method for unsupported formats."""
        loader = DocumentLoader()
        
        assert loader.can_load("document.unsupported") is False
        assert loader.can_load("document") is False
        assert loader.can_load("") is False
    
    def test_file_hash_calculation(self, sample_text_file):
        """Test file hash calculation."""
        loader = DocumentLoader()
        file_hash = loader.calculate_file_hash(sample_text_file)
        
        assert isinstance(file_hash, str)
        assert len(file_hash) == 64  # SHA-256 hex length
        # Same file should have same hash
        assert file_hash == loader.calculate_file_hash(sample_text_file)
    
    def test_basic_metadata_extraction(self, sample_text_file):
        """Test basic file metadata extraction."""
        loader = DocumentLoader()
        metadata = loader.extract_basic_metadata(sample_text_file)
        
        assert metadata["filename"] == sample_text_file.name
        assert metadata["file_size_bytes"] > 0
        assert "created_timestamp" in metadata
        assert "modified_timestamp" in metadata
        assert metadata["absolute_path"] == str(sample_text_file.absolute())
    
    def test_mime_type_detection(self):
        """Test MIME type detection."""
        loader = DocumentLoader()
        
        # Test known extensions
        assert loader.get_mime_type("doc.pdf") == "application/pdf"
        assert loader.get_mime_type("doc.docx") == \
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert loader.get_mime_type("doc.txt") == "text/plain"
        
        # Test unknown extension
        assert loader.get_mime_type("doc.unknown") == "application/octet-stream"


class TestTextDocumentLoader:
    """Test text document loader."""
    
    def test_load_text_document(self, sample_text_file):
        """Test loading a text document."""
        loader = TextDocumentLoader()
        result = loader.load_document(sample_text_file)
        
        assert "content" in result
        assert "metadata" in result
        
        content = result["content"]
        metadata = result["metadata"]
        
        # Check content
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Test Research Paper" in content
        
        # Check metadata
        assert metadata["mime_type"] == "text/plain"
        assert "file_hash" in metadata
        assert metadata["character_count"] == len(content)
        assert metadata["line_count"] > 0
    
    def test_text_loader_cannot_load_pdf(self):
        """Test text loader rejects non-text files."""
        loader = TextDocumentLoader()
        assert loader.can_load("document.pdf") is True  # It can load PDFs (inherited)
        
        # But load_document will fail for PDFs without PyMuPDF
        with pytest.raises(Exception):
            with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
                loader.load_document(f.name)


class TestPDFDocumentLoader:
    """Test PDF document loader."""
    
    @patch('provenanceai.ingestion.document_loader.fitz')
    def test_load_pdf_document(self, mock_fitz, sample_pdf_metadata):
        """Test loading a PDF document with mocked PyMuPDF."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF page content"
        mock_doc.__len__.return_value = 5
        
        mock_doc.load_page.return_value = mock_page
        mock_doc.metadata = sample_pdf_metadata
        
        mock_fitz.open.return_value = mock_doc
        
        # Create loader and test
        loader = PDFDocumentLoader()
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            result = loader.load_document(f.name)
        
        assert "content" in result
        assert "metadata" in result
        assert result["metadata"]["mime_type"] == "application/pdf"
        assert result["metadata"]["page_count"] == 5
        assert "author" in result["metadata"]
        
        # Verify close was called
        mock_doc.close.assert_called_once()
    
    def test_pdf_loader_import_error(self):
        """Test error when PyMuPDF is not installed."""
        loader = PDFDocumentLoader()
        
        # Remove the imported module
        loader._pymupdf = None
        
        with patch.dict('sys.modules', {'fitz': None}):
            with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
                with pytest.raises(ImportError) as exc_info:
                    loader.load_document(f.name)
                
                assert "PyMuPDF (fitz) is required" in str(exc_info.value)


class TestDocumentLoaderFactory:
    """Test document loader factory."""
    
    def test_get_loader_for_supported_formats(self):
        """Test factory returns correct loader for file types."""
        # Text files
        loader = DocumentLoaderFactory.get_loader("document.txt")
        assert isinstance(loader, TextDocumentLoader)
        
        # PDF files
        loader = DocumentLoaderFactory.get_loader("document.pdf")
        assert isinstance(loader, PDFDocumentLoader)
        
        # DOCX files
        loader = DocumentLoaderFactory.get_loader("document.docx")
        assert isinstance(loader, DOCXDocumentLoader)
    
    def test_get_loader_unsupported_format(self):
        """Test factory raises error for unsupported formats."""
        with pytest.raises(ValueError) as exc_info:
            DocumentLoaderFactory.get_loader("document.unsupported")
        
        assert "Unsupported file type" in str(exc_info.value)
    
    @patch('provenanceai.ingestion.document_loader.PDFDocumentLoader')
    def test_load_document_via_factory(self, mock_pdf_loader):
        """Test loading document through factory."""
        # Mock the PDF loader
        mock_loader_instance = Mock()
        mock_loader_instance.load_document.return_value = {
            'content': 'Test content',
            'metadata': {'test': 'data'}
        }
        mock_pdf_loader.return_value = mock_loader_instance
        
        # Test factory method
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            result = DocumentLoaderFactory.load_document(f.name)
        
        assert result['content'] == 'Test content'
        assert result['metadata']['test'] == 'data'