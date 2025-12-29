# File: tests/unit/test_error_handling.py


"""
Tests for error handling and edge cases.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch

from provenanceai import analyze

from provenanceai.utils.exceptions import (
    DocumentLoadError,
    InferenceError,
    ValidationError,
)
from provenanceai.utils.validation import validate_file_path, validate_config_dict


if os.name == "nt":
    pytest.skip("chmod-based permission test is unreliable on Windows", allow_module_level=True)

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_validate_file_path(self):
        """Test file path validation."""
        # Valid file
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"x")
            f.flush()
            path = validate_file_path(f.name)
            assert isinstance(path, Path)
        
        # Non-existent file
        with pytest.raises(DocumentLoadError) as exc_info:
            validate_file_path("/non/existent/path")
        assert "does not exist" in str(exc_info.value)
        
        # Directory instead of file
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises(DocumentLoadError) as exc_info:
                validate_file_path(d)
            assert "not a file" in str(exc_info.value)
        
        # Empty file
        with tempfile.NamedTemporaryFile() as f:
            # Truncate to make it empty
            f.seek(0)
            f.truncate()
            with pytest.raises(DocumentLoadError) as exc_info:
                validate_file_path(f.name)
            assert "empty" in str(exc_info.value)
        
        # File too large (create a large file)
        with tempfile.NamedTemporaryFile() as f:
            # Write 101MB of data
            f.write(b'0' * (101 * 1024 * 1024))
            f.flush()
            
            with pytest.raises(DocumentLoadError) as exc_info:
                validate_file_path(f.name)
            assert "too large" in str(exc_info.value)
    
    def test_validate_config_dict(self):
        """Test configuration validation."""
        # Valid config
        valid_config = {
            'trust_scoring': {
                'weights': {
                    'authority': 0.3,
                    'document_type': 0.2,
                    'review': 0.25,
                    'currency': 0.15,
                    'completeness': 0.1,
                }
            },
            'policy': {}
        }
        
        validate_config_dict(valid_config)  # Should not raise
        
        # Missing required section
        invalid_config = {'trust_scoring': {}}
        with pytest.raises(ValidationError) as exc_info:
            validate_config_dict(invalid_config)
        assert "Missing configuration section" in str(exc_info.value)
        
        # Invalid weights (don't sum to 1.0)
        invalid_weights = {
            'trust_scoring': {
                'weights': {'authority': 0.5, 'document_type': 0.6}
            },
            'policy': {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_config_dict(invalid_weights)
        assert "must sum to 1.0" in str(exc_info.value)
    
    def test_corrupted_pdf_handling(self):
        """Test handling of corrupted PDF files."""
        # Create a file that looks like PDF but is corrupted
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4\n%%Corrupted PDF content\n')
            corrupted_pdf = Path(f.name)
        
        try:
            # Should raise an appropriate error
            with pytest.raises(Exception) as exc_info:
                analyze(corrupted_pdf)
            # Don't assert specific error type since it could be from PyMuPDF
            assert exc_info.value is not None
        finally:
            corrupted_pdf.unlink()
    
    @patch('provenanceai.api.DocumentLoaderFactory')
    def test_loader_exception_propagation(self, mock_factory):
        """Test that loader exceptions are properly propagated."""
        mock_factory.load_document.side_effect = Exception("Loader failed")
        
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            with pytest.raises(Exception) as exc_info:
                analyze(f.name)
            
            assert "Loader failed" in str(exc_info.value)
    
    def test_permission_denied_file(self):
        """Test handling of permission-denied files (Unix-like systems)."""
        if hasattr(os, 'chmod'):
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b"Test content")
                no_permission_file = Path(f.name)
            
            try:
                # Remove read permissions
                os.chmod(no_permission_file, 0o000)
                
                with pytest.raises(Exception) as exc_info:
                    analyze(no_permission_file)
                # Should raise some kind of permission error
                assert exc_info.value is not None
            finally:
                # Restore permissions so we can delete
                os.chmod(no_permission_file, 0o644)
                no_permission_file.unlink()
    
    def test_analyze_with_malformed_config(self):
        """Test analyze() with malformed configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("malformed: yaml: content: that: is: invalid")
            bad_config = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as doc_file:
            doc_file.write("Test content")
            doc_file.flush()
            
            try:
                # Should raise YAML parsing error
                with pytest.raises(Exception) as exc_info:
                    analyze(doc_file.name, config_path=bad_config)
                assert exc_info.value is not None
            finally:
                bad_config.unlink()
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters in documents."""
        unicode_content = """
        Document with Unicode: 
        • Bullet points
        🌍 Emojis
        中文 Chinese characters
        العربية Arabic script
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write(unicode_content)
            unicode_file = Path(f.name)
        
        try:
            report = analyze(unicode_file)
            assert isinstance(report, object)
            
            # JSON serialization should handle Unicode
            json_output = report.to_json()
            parsed = json.loads(json_output)
            assert parsed is not None
            
        finally:
            unicode_file.unlink()