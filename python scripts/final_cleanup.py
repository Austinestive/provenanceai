# File: scripts/final_cleanup.py
#!/usr/bin/env python3
"""Final cleanup of linting issues."""

from pathlib import Path
import re

def fix_file(filepath, fixes):
    """Apply fixes to a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_init_py():
    """Fix __init__.py issues."""
    fixes = [
        # Break long line
        (r'__description__ = "A standard, explainable way for AI systems to understand provenance and trustworthiness of knowledge sources"',
         '__description__ = (\n    "A standard, explainable way for AI systems to understand provenance "\n    "and trustworthiness of knowledge sources"\n)'),
        
        # Fix duplicate import
        (r'from \.api import analyze, ProvenanceReport\nfrom \.core\.schema import \(\n    ProvenanceReport,',
         'from .api import analyze\nfrom .core.schema import (\n    ProvenanceReport,')
    ]
    
    fixed = fix_file("src/provenanceai/__init__.py", fixes)
    if fixed:
        print("✅ Fixed __init__.py")

def fix_api_py():
    """Fix api.py issues."""
    fixes = [
        # Remove unused json import
        (r'import json\n', ''),
        
        # Fix duplicate json import
        (r'def _load_config\(config_path: Union\[str, Path\]\) -> dict:\n    """Load configuration from file."""\n    import json\n',
         'def _load_config(config_path: Union[str, Path]) -> dict:\n    """Load configuration from file."""\n'),
        
        # Fix undefined names by adding imports
        (r'from \.core\.schema import ProvenanceReport\n',
         'from .core.schema import ProvenanceReport, IdentityBlock, ContentBlock, TechnicalBlock\n'),
        
        # Fix bare except
        (r'except:\n\s+language = "unknown"',
         'except Exception:\n        language = "unknown"')
    ]
    
    fixed = fix_file("src/provenanceai/api.py", fixes)
    if fixed:
        print("✅ Fixed api.py")

def fix_config_init_py():
    """Fix config/__init__.py."""
    fixes = [
        # Remove unused Optional import
        (r'from typing import Dict, Any, Optional\n',
         'from typing import Dict, Any\n')
    ]
    
    fixed = fix_file("src/provenanceai/config/__init__.py", fixes)
    if fixed:
        print("✅ Fixed config/__init__.py")

def fix_core_schema_py():
    """Fix core/schema.py."""
    fixes = [
        # Remove unused Union import
        (r'from typing import Optional, List, Dict, Any, Union\n',
         'from typing import Optional, List, Dict, Any\n'),
        
        # Break long line
        (r'result\[key\] = \{k: v\.to_dict\(\) if hasattr\(v, \'to_dict\'\) else v\n\s+for k, v in value\.items\(\)\}',
         'result[key] = {\n                k: v.to_dict() if hasattr(v, \'to_dict\') else v\n                for k, v in value.items()\n            }')
    ]
    
    fixed = fix_file("src/provenanceai/core/schema.py", fixes)
    if fixed:
        print("✅ Fixed core/schema.py")

def fix_inference_py():
    """Fix provenance_inferencer.py."""
    fixes = [
        # Remove unused import
        (r'from dataclasses import asdict\n\n', ''),
        
        # Remove unused variable
        (r'\s+metadata_lower = \{k: str\(v\)\.lower\(\) for k, v in metadata\.items\(\) if v\}\n\n',
         '\n')
    ]
    
    fixed = fix_file("src/provenanceai/inference/provenance_inferencer.py", fixes)
    if fixed:
        print("✅ Fixed provenance_inferencer.py")

def fix_ingestion_py():
    """Fix document_loader.py."""
    fixes = [
        # Remove unused imports
        (r'import os\n', ''),
        (r'from typing import Optional, Dict, Any, BinaryIO, Union\n',
         'from typing import Dict, Any, Union\n'),
        
        # Break long lines
        (r'application/vnd\.openxmlformats-officedocument\.wordprocessingml\.document',
         'application/vnd.openxmlformats-officedocument.'
         'wordprocessingml.document'),
        
        (r'"application/vnd\.openxmlformats-officedocument\.wordprocessingml\.document",',
         '"application/vnd.openxmlformats-officedocument.'
         'wordprocessingml.document",'),
        
        (r'raise ImportError\(\n\s+"PyMuPDF \(fitz\) is required for PDF loading\. "',
         'raise ImportError("PyMuPDF (fitz) is required for PDF loading. "')
    ]
    
    fixed = fix_file("src/provenanceai/ingestion/document_loader.py", fixes)
    if fixed:
        print("✅ Fixed document_loader.py")

def fix_integration_py():
    """Fix rag_adapters.py."""
    fixes = [
        # Remove unused import
        (r'from typing import Dict, Any, List\n',
         'from typing import Dict, Any\n'),
        
        # Fix undefined name - add import
        (r'from \.\.core\.schema import ProvenanceReport\n',
         'from ..core.schema import ProvenanceReport, AIUsagePermission\n')
    ]
    
    fixed = fix_file("src/provenanceai/integration/rag_adapters.py", fixes)
    if fixed:
        print("✅ Fixed rag_adapters.py")

def fix_policy_engine_py():
    """Fix ai_policy_engine.py."""
    fixes = [
        # Remove unused imports
        (r'from dataclasses import asdict\n', ''),
        (r'from typing import Dict, Any, List, Optional\n',
         'from typing import Dict, Any, Optional\n'),
        
        # Remove unused re import
        (r'\s+import re\n', '')
    ]
    
    fixed = fix_file("src/provenanceai/policy/ai_policy_engine.py", fixes)
    if fixed:
        print("✅ Fixed ai_policy_engine.py")

def fix_trust_scoring_py():
    """Fix scoring_engine.py."""
    fixes = [
        # Remove unused imports
        (r'from dataclasses import asdict\n', ''),
        (r'from datetime import datetime, timezone\n',
         'from datetime import timezone\n'),
        (r'from typing import Dict, Any, List, Optional\n',
         'from typing import Dict, Any, Optional\n'),
        
        # Fix duplicate import
        (r'def _calculate_currency_score\(self, provenance: ProvenanceBlock\) -> TrustScore:\n\s+"""Calculate score based on document currency \(age\)."""\n\s+score = 0\.5\n\s+rule_applied = "default_neutral"\n\s+\n\s+if provenance\.publication_date:\n\s+from datetime import datetime\n',
         'def _calculate_currency_score(self, provenance: ProvenanceBlock) -> TrustScore:\n        """Calculate score based on document currency (age)."""\n        score = 0.5\n        rule_applied = "default_neutral"\n\n        if provenance.publication_date:\n            from datetime import datetime\n')
    ]
    
    fixed = fix_file("src/provenanceai/trust/scoring_engine.py", fixes)
    if fixed:
        print("✅ Fixed scoring_engine.py")

def fix_utils_caching_py():
    """Fix caching.py."""
    fixes = [
        # Remove unused imports
        (r'from functools import lru_cache\n', ''),
        (r'from typing import Any, Callable, Optional\n',
         'from typing import Any, Optional\n')
    ]
    
    fixed = fix_file("src/provenanceai/utils/caching.py", fixes)
    if fixed:
        print("✅ Fixed caching.py")

def fix_utils_exceptions_py():
    """Fix exceptions.py."""
    fixes = [
        # Remove duplicate imports at bottom
        (r'\nfrom \.\.ingestion\.document_loader import DocumentLoaderFactory\nfrom \.validation import validate_file_path, validate_config_dict\n',
         '')
    ]
    
    fixed = fix_file("src/provenanceai/utils/exceptions.py", fixes)
    if fixed:
        print("✅ Fixed exceptions.py")

def run_final_validation():
    """Run final validation tests."""
    print("\n" + "=" * 60)
    print("FINAL VALIDATION")
    print("=" * 60)
    
    import subprocess
    import sys
    
    tests = [
        ("Import test", [sys.executable, "-c", "import provenanceai; print(f'Version: {provenanceai.__version__}')"]),
        ("Black formatting", [sys.executable, "-m", "black", "--check", "src/provenanceai"]),
        ("Import sorting", [sys.executable, "-m", "isort", "--check-only", "src/provenanceai"]),
        ("Unit tests", [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"]),
        ("Build package", [sys.executable, "-m", "build"]),
    ]
    
    all_passed = True
    
    for name, cmd in tests:
        print(f"\n▶ {name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ PASSED")
            if result.stdout.strip():
                print(f"   Output: {result.stdout[:100]}...")
        else:
            print(f"   ❌ FAILED")
            if result.stderr:
                error = result.stderr[:200]
                print(f"   Error: {error}...")
            all_passed = False
    
    return all_passed

def main():
    """Run all cleanup tasks."""
    print("🔧 Final cleanup of linting issues...")
    print("=" * 60)
    
    # Fix all files
    fix_init_py()
    fix_api_py()
    fix_config_init_py()
    fix_core_schema_py()
    fix_inference_py()
    fix_ingestion_py()
    fix_integration_py()
    fix_policy_engine_py()
    fix_trust_scoring_py()
    fix_utils_caching_py()
    fix_utils_exceptions_py()
    
    print("\n" + "=" * 60)
    print("Applying final formatting...")
    print("=" * 60)
    
    # Apply final formatting
    import subprocess
    subprocess.run(["black", "src/provenanceai"], capture_output=True)
    print("✅ Applied black formatting")
    
    subprocess.run(["isort", "src/provenanceai"], capture_output=True)
    print("✅ Applied import sorting")
    
    # Run final validation
    if run_final_validation():
        print("\n" + "=" * 60)
        print("🎉 ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nProvenanceAI is READY FOR RELEASE! 🚀")
        
        print("\n📋 Final steps:")
        print("1. Check version in pyproject.toml")
        print("2. Create release notes (CHANGELOG.md)")
        print("3. Upload to PyPI: twine upload dist/*")
        print("4. Create GitHub release")
        
        # Show package info
        print("\n📦 Package info:")
        dist_dir = Path("dist")
        if dist_dir.exists():
            files = list(dist_dir.glob("*"))
            for file in files:
                size_mb = file.stat().st_size / 1024 / 1024
                print(f"  - {file.name} ({size_mb:.2f} MB)")
    else:
        print("\n" + "=" * 60)
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 60)
        print("\nRun: flake8 src/provenanceai")
        print("To see remaining issues.")

if __name__ == "__main__":
    main()