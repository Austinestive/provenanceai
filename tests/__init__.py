# File: tests/__init__.py
"""
Test package for ProvenanceAI.
"""

# Make tests discoverable

# File: run_tests.py (at project root)
#!/usr/bin/env python3
"""
Test runner script for ProvenanceAI.
Run with: python run_tests.py [options]
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests based on type."""
    base_cmd = ["pytest"]
    
    if verbose:
        base_cmd.append("-v")
    
    if coverage:
        base_cmd.extend(["--cov=provenanceai", "--cov-report=term-missing"])
    
    test_paths = {
        "all": ["tests/"],
        "unit": ["tests/unit/"],
        "integration": ["tests/integration/"],
        "performance": ["tests/performance/", "-m", "benchmark"],
        "schema": ["tests/unit/test_core_schema.py"],
        "ingestion": ["tests/unit/test_document_ingestion.py"],
        "inference": ["tests/unit/test_provenance_inference.py"],
        "trust": ["tests/unit/test_trust_scoring.py"],
        "api": ["tests/integration/test_api.py"],
        "errors": ["tests/unit/test_error_handling.py"],
    }
    
    if test_type not in test_paths:
        print(f"Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_paths.keys())}")
        return False
    
    cmd = base_cmd + test_paths[test_type]
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run ProvenanceAI tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        help="Type of tests to run (all, unit, integration, etc.)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--list", action="store_true", help="List available test types")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available test types:")
        print("  all         - Run all tests")
        print("  unit        - Unit tests only")
        print("  integration - Integration tests only")
        print("  performance - Performance benchmarks")
        print("  schema      - Core schema tests")
        print("  ingestion   - Document ingestion tests")
        print("  inference   - Provenance inference tests")
        print("  trust       - Trust scoring tests")
        print("  api         - API integration tests")
        print("  errors      - Error handling tests")
        return 0
    
    success = run_tests(args.test_type, args.verbose, args.coverage)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())