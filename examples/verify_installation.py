# File: examples/verify_installation.py
"""
Verify ProvenanceAI installation works.
"""

import tempfile
from pathlib import Path

try:
    from provenanceai import analyze
    print("[OK] ProvenanceAI imported successfully")
    
    # Create test document
    test_content = """
    Test Research Document
    Author: Dr. Test Researcher
    Date: 2023-01-15
    This is a test document.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file = Path(f.name)
    
    try:
        # Test analysis
        report = analyze(test_file)
        print("[OK] Document analysis successful")
        
        # Test basic attributes
        print(f"[OK] Document ID: {report.identity.document_id}")
        print(f"[OK] Trust score: {report.trust.overall_score.score if report.trust.overall_score else 'N/A'}")
        
        # Test JSON serialization
        json_output = report.to_json()
        print(f"[OK] JSON serialization works ({len(json_output)} chars)")
        
        print("\n" + "=" * 50)
        print("SUCCESS: ProvenanceAI is working correctly!")
        print("=" * 50)
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            
except ImportError as e:
    print(f"[ERROR] Failed to import provenanceai: {e}")
    print("\nTry: pip install -e .")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")