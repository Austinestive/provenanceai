# File: tests/integration/test_api.py
"""
Integration tests for the main ProvenanceAI API.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from provenanceai import analyze
from provenanceai.api import _load_config, _check_for_references, _check_for_citations
from provenanceai.core.schema import ProvenanceReport


class TestMainAPI:
    """Test the main analyze() API function."""
    
    def test_analyze_text_file(self, sample_text_file):
        """Test analyzing a text file."""
        report = analyze(sample_text_file)
        
        assert isinstance(report, ProvenanceReport)
        assert report.identity.original_filename == sample_text_file.name
        assert report.trust.overall_score is not None
        assert 0 <= report.trust.overall_score.score <= 1.0
        
        # Test JSON serialization
        json_output = report.to_json()
        parsed = json.loads(json_output)
        
        assert 'identity' in parsed
        assert 'provenance' in parsed
        assert 'trust' in parsed
        assert 'ai_use' in parsed
        assert 'explainability' in parsed
        assert 'technical' in parsed
    
    def test_analyze_with_config(self, sample_text_file, sample_config_yaml):
        """Test analyzing with custom YAML configuration."""
        report = analyze(sample_text_file, config_path=sample_config_yaml)
        
        assert isinstance(report, ProvenanceReport)
        # Custom weights should affect scores
        # (We can't assert specific values since they depend on inference)
    
    @patch('provenanceai.api.DocumentLoaderFactory')
    def test_analyze_mocked_loader(self, mock_factory):
        """Test analyze with mocked document loader."""
        # Mock the loader response
        mock_loader = Mock()
        mock_loader.load_document.return_value = {
            'content': 'Test content with references.',
            'metadata': {
                'filename': 'test.pdf',
                'file_size_bytes': 1000,
                'author': 'Test Author',
                'title': 'Test Document',
            }
        }
        mock_factory.load_document.return_value = mock_loader.load_document.return_value
        
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            report = analyze(f.name)
        
        assert isinstance(report, ProvenanceReport)
        mock_factory.load_document.assert_called_once()
    
    def test_file_not_found_error(self):
        """Test error handling for non-existent files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            analyze("/non/existent/path/document.pdf")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_unsupported_file_type(self):
        """Test error handling for unsupported file types."""
        with tempfile.NamedTemporaryFile(suffix='.unsupported') as f:
            with pytest.raises(ValueError) as exc_info:
                analyze(f.name)
        
        assert "unsupported" in str(exc_info.value).lower()
    
    def test_load_config_yaml(self, sample_config_yaml):
        """Test loading YAML configuration."""
        config = _load_config(sample_config_yaml)
        
        assert isinstance(config, dict)
        assert 'trust_scoring' in config
        assert 'weights' in config['trust_scoring']
        assert config['trust_scoring']['weights']['authority'] == 0.35
    
    def test_load_config_json(self):
        """Test loading JSON configuration."""
        config_data = {
            "trust_scoring": {
                "weights": {"authority": 0.4}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            config = _load_config(config_path)
            assert config['trust_scoring']['weights']['authority'] == 0.4
        finally:
            config_path.unlink()
    
    def test_load_config_unsupported_format(self):
        """Test error for unsupported config format."""
        with tempfile.NamedTemporaryFile(suffix='.xml') as f:
            config_path = Path(f.name)
            with pytest.raises(ValueError) as exc_info:
                _load_config(config_path)
            
            assert "unsupported" in str(exc_info.value).lower()
    
    def test_check_for_references(self):
        """Test reference detection."""
        content_with_refs = """
        Introduction...
        References:
        1. Author (2022) Title
        2. Another (2021) Paper
        """
        
        content_without_refs = "Just some text without references."
        
        assert _check_for_references(content_with_refs) is True
        assert _check_for_references(content_without_refs) is False
    
    def test_check_for_citations(self):
        """Test citation detection."""
        content_with_citations = """
        Previous work (Smith, 2022) shows that...
        As demonstrated by Jones et al. [2021]...
        In 2019, researchers found...
        """
        
        content_without_citations = "Just some text without citations."
        
        assert _check_for_citations(content_with_citations) is True
        assert _check_for_citations(content_without_citations) is False
    
    def test_analyze_empty_file(self):
        """Test analyzing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            empty_file = Path(f.name)
        
        try:
            with pytest.raises(Exception) as exc_info:
                analyze(empty_file)
            # Should raise some error about empty file
        finally:
            empty_file.unlink()
    
    @pytest.mark.slow
    def test_analyze_large_file_handling(self):
        """Test handling of large files (marked as slow)."""
        # Create a large file (but not too large for tests)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write 10KB of data
            for i in range(1000):
                f.write("Line {}: Some test content for provenance analysis.\n".format(i))
            large_file = Path(f.name)
        
        try:
            report = analyze(large_file)
            assert isinstance(report, ProvenanceReport)
            # Should complete without memory issues
        finally:
            large_file.unlink()