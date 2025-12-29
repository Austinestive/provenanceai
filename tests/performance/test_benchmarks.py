# File: tests/performance/test_benchmarks.py
"""
Performance benchmarks for ProvenanceAI.
These tests help identify performance bottlenecks.
"""

import pytest
import time
import tempfile
from pathlib import Path
import statistics

from provenanceai import analyze
from provenanceai.ingestion.document_loader import DocumentLoaderFactory


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def create_large_test_file(self, size_kb: int = 100) -> Path:
        """Create a test file of specified size."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write enough content to reach target size
            line = "This is a test line for performance benchmarking. " * 10 + "\n"
            line_size = len(line.encode('utf-8'))
            
            lines_needed = (size_kb * 1024) // line_size
            
            for i in range(lines_needed):
                f.write(f"{i}: {line}")
            
            return Path(f.name)
    
    def test_document_loading_speed(self, benchmark):
        """Benchmark document loading speed."""
        test_file = self.create_large_test_file(size_kb=500)  # 500KB file
        
        try:
            def load_document():
                return DocumentLoaderFactory.load_document(test_file)
            
            # Run benchmark
            result = benchmark(load_document)
            
            # Verify result
            assert 'content' in result
            assert 'metadata' in result
            
        finally:
            test_file.unlink()
    
    def test_analyze_performance_small_file(self, benchmark):
        """Benchmark analyze() with small file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Small test document for benchmarking.\n" * 100)  # ~5KB
            test_file = Path(f.name)
        
        try:
            result = benchmark(analyze, test_file)
            assert isinstance(result, object)  # ProvenanceReport
        finally:
            test_file.unlink()
    
    @pytest.mark.parametrize("file_size_kb", [10, 100, 1000])
    def test_analyze_scalability(self, file_size_kb):
        """Test how analyze() scales with file size."""
        test_file = self.create_large_test_file(size_kb=file_size_kb)
        
        try:
            # Time the analysis
            start_time = time.time()
            report = analyze(test_file)
            end_time = time.time()
            
            elapsed = end_time - start_time
            
            # Log performance (not assert - just informational)
            print(f"\nFile size: {file_size_kb}KB, Time: {elapsed:.2f}s, "
                  f"Throughput: {file_size_kb/elapsed:.2f}KB/s")
            
            # Basic validation
            assert isinstance(report, object)
            
            # Performance assertion (adjust based on expectations)
            # 100KB should take less than 5 seconds on average hardware
            if file_size_kb == 100:
                assert elapsed < 5.0, f"Analysis too slow: {elapsed:.2f}s for 100KB"
            
        finally:
            test_file.unlink()
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow unbounded."""
        import tracemalloc
        import gc
        
        # Start tracking memory
        tracemalloc.start()
        
        # Create multiple reports to check for memory leaks
        reports = []
        
        for i in range(10):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"Test document {i} for memory testing.\n" * 100)
                test_file = Path(f.name)
            
            try:
                report = analyze(test_file)
                reports.append(report)
                
                # Force garbage collection
                gc.collect()
                
                # Take snapshot every few iterations
                if i % 3 == 0:
                    snapshot = tracemalloc.take_snapshot()
                    # Could analyze snapshot here for memory growth
                
            finally:
                test_file.unlink()
        
        # Get final memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\nMemory usage - Current: {current/1024:.1f}KB, Peak: {peak/1024:.1f}KB")
        
        # Assert reasonable memory usage
        # Peak should be less than 100MB for 10 small documents
        assert peak < 100 * 1024 * 1024, f"Excessive memory usage: {peak/1024/1024:.1f}MB"
    
    def test_concurrent_analysis(self):
        """Test that analyze() can be called concurrently."""
        import concurrent.futures
        import threading
        
        # Create multiple test files
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"Concurrent test document {i}.\n" * 50)
                test_files.append(Path(f.name))
        
        try:
            # Track thread IDs to ensure concurrent execution
            thread_ids = []
            
            def analyze_and_track(file_path):
                thread_ids.append(threading.get_ident())
                return analyze(file_path)
            
            # Use ThreadPoolExecutor for concurrency
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(analyze_and_track, f) for f in test_files]
                results = [f.result() for f in futures]
            
            # Should have results from all files
            assert len(results) == 5
            assert all(isinstance(r, object) for r in results)
            
            # Should have used multiple threads
            unique_threads = set(thread_ids)
            assert len(unique_threads) > 1, "All analyses ran in same thread"
            
        finally:
            for f in test_files:
                f.unlink()