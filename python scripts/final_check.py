# File: scripts/final_check.py
#!/usr/bin/env python3
"""Final check before release."""

import subprocess
import sys

def run(cmd):
    """Run command and return success."""
    print(f"\n▶ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Success")
        return True
    else:
        print(f"❌ Failed: {result.stderr[:200]}")
        return False

def main():
    print("🔍 Final Pre-Release Check")
    print("=" * 60)
    
    checks = []
    
    # Basic import test
    print("\n1. Testing imports...")
    try:
        import provenanceai
        print(f"✅ Import works: {provenanceai.__version__}")
        checks.append(True)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        checks.append(False)
    
    # Run key validation steps
    checks.append(run([sys.executable, "-m", "black", "--check", "src/provenanceai"]))
    checks.append(run([sys.executable, "-m", "isort", "--check-only", "src/provenanceai"]))
    checks.append(run([sys.executable, "-m", "mypy", "src/provenanceai", "--config-file", "mypy.ini"]))
    checks.append(run([sys.executable, "-m", "flake8", "src/provenanceai"]))
    
    # Build test
    checks.append(run([sys.executable, "-m", "build"]))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 READY FOR RELEASE!")
        print("\nNext steps:")
        print("1. Update version in pyproject.toml if needed")
        print("2. Create release notes")
        print("3. Upload to PyPI: twine upload dist/*")
        return 0
    else:
        print("\n⚠️  Needs more work")
        return 1

if __name__ == "__main__":
    sys.exit(main())