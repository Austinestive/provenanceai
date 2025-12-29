# File: scripts/validate_release_fixed.py
#!/usr/bin/env python3
"""
Fixed validation script without emojis for Windows.
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import yaml

def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n[CHECK] {description}...")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("   [PASS]")
        if result.stdout.strip():
            print(f"   Output: {result.stdout[:200]}...")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [FAIL]")
        if e.stderr:
            error_lines = e.stderr.strip().split('\n')
            for line in error_lines[:5]:
                print(f"   {line}")
            if len(error_lines) > 5:
                print(f"   ... and {len(error_lines) - 5} more lines")
        return False
    except FileNotFoundError:
        print(f"   [ERROR] Command not found: {cmd[0]}")
        print(f"   Install with: pip install {cmd[0]}")
        return False

def check_files():
    """Check required files exist."""
    print("\n" + "=" * 80)
    print("FILE CHECK")
    print("=" * 80)
    
    required_files = [
        ("pyproject.toml", "Package configuration"),
        ("src/provenanceai/__init__.py", "Main package init"),
        ("src/provenanceai/api.py", "Main API"),
        ("src/provenanceai/core/schema.py", "Core schema"),
        ("README.md", "Documentation"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"[OK] {description}: {file_path}")
        else:
            print(f"[MISSING] {description}: {file_path}")
            all_exist = False
    
    return all_exist

def run_validation():
    """Run comprehensive validation."""
    print("\n" + "=" * 80)
    print("RUNNING VALIDATION CHECKS")
    print("=" * 80)
    
    checks = [
        ("Unit Tests", ["pytest", "tests/unit/", "-v", "--tb=short"]),
        ("Integration Tests", ["pytest", "tests/integration/", "-v", "--tb=short"]),
        ("Type Checking", ["mypy", "src/provenanceai", "--ignore-missing-imports"]),
        ("Linting", ["flake8", "src/provenanceai"]),
        ("Formatting", ["black", "--check", "src/provenanceai"]),
        ("Imports", ["isort", "--check-only", "src/provenanceai"]),
    ]
    
    results = []
    
    for name, cmd in checks:
        success = run_command(cmd, name)
        results.append((name, success))
    
    return results

def build_package():
    """Test package building."""
    print("\n" + "=" * 80)
    print("PACKAGE BUILD TEST")
    print("=" * 80)
    
    # Clean dist directory first
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.glob("*"):
            try:
                file.unlink()
            except:
                pass
    
    # Build package
    if run_command([sys.executable, "-m", "build"], "Building package"):
        # Check what was built
        if dist_dir.exists():
            files = list(dist_dir.glob("*"))
            print(f"\n[INFO] Built {len(files)} distribution files:")
            for file in files:
                size_kb = file.stat().st_size / 1024
                print(f"  - {file.name} ({size_kb:.1f} KB)")
            return True
        else:
            print("[WARN] dist/ directory not created")
            return False
    return False

def test_installation():
    """Test installation from built package."""
    print("\n" + "=" * 80)
    print("INSTALLATION TEST")
    print("=" * 80)
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("[SKIP] No dist directory")
        return False
    
    # Find wheel file
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("[SKIP] No wheel files found")
        return False
    
    wheel_file = wheel_files[0]
    print(f"[INFO] Testing installation of: {wheel_file.name}")
    
    # Create a test virtual environment
    test_venv = Path("test_install_venv")
    
    try:
        # Clean up old test venv
        if test_venv.exists():
            import shutil
            shutil.rmtree(test_venv)
        
        # Create new venv
        print("[INFO] Creating test virtual environment...")
        venv_cmd = [sys.executable, "-m", "venv", str(test_venv)]
        subprocess.run(venv_cmd, capture_output=True, check=True)
        
        # Install package in test venv
        pip_path = test_venv / "Scripts" / "pip.exe"
        install_cmd = [str(pip_path), "install", str(wheel_file)]
        
        print(f"[INFO] Installing package...")
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print("[PASS] Installation successful")
            
            # Test import
            python_path = test_venv / "Scripts" / "python.exe"
            test_script = """
import provenanceai
print(f"ProvenanceAI version: {provenanceai.__version__}")
print(f"ProvenanceAI description: {provenanceai.__description__}")
"""
            
            test_cmd = [str(python_path), "-c", test_script]
            import_result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if import_result.returncode == 0:
                print("[PASS] Import successful")
                print(f"Output: {import_result.stdout}")
                return True
            else:
                print("[FAIL] Import failed")
                print(f"Error: {import_result.stderr}")
                return False
        else:
            print("[FAIL] Installation failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    finally:
        # Cleanup
        if test_venv.exists():
            import shutil
            try:
                shutil.rmtree(test_venv)
                print("[INFO] Cleaned up test virtual environment")
            except:
                print("[WARN] Could not clean up test virtual environment")

def main():
    """Main validation function."""
    print("\n" + "=" * 80)
    print("PROVENANCEAI RELEASE VALIDATION")
    print("=" * 80)
    
    # Step 1: Check files
    if not check_files():
        print("\n[ERROR] Critical files missing!")
        return False
    
    # Step 2: Run validation checks
    results = run_validation()
    
    # Step 3: Build package
    build_success = build_package()
    
    # Step 4: Test installation (if build succeeded)
    install_success = False
    if build_success:
        install_success = test_installation()
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    passed_checks = sum(1 for _, success in results if success)
    total_checks = len(results)
    
    print(f"\nCode Quality: {passed_checks}/{total_checks} checks passed")
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nPackaging:")
    print(f"  {'[PASS]' if build_success else '[FAIL]'} Package builds")
    print(f"  {'[PASS]' if install_success else '[FAIL]'} Installation works")
    
    # Overall assessment
    overall_passed = (passed_checks == total_checks) and build_success and install_success
    
    if overall_passed:
        print("\n" + "=" * 80)
        print("SUCCESS: READY FOR RELEASE!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Update version in pyproject.toml")
        print("2. Create release notes")
        print("3. Upload to PyPI: twine upload dist/*")
        print("4. Create GitHub release")
        return True
    else:
        print("\n" + "=" * 80)
        print("NOT READY FOR RELEASE")
        print("=" * 80)
        
        issues = []
        if passed_checks < total_checks:
            issues.append(f"Code quality checks failed ({passed_checks}/{total_checks})")
        if not build_success:
            issues.append("Package build failed")
        if not install_success:
            issues.append("Installation test failed")
        
        print("\nIssues to fix:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\nQuick fix commands:")
        print("  pip install pytest pytest-cov mypy flake8 black isort build twine")
        print("  pip install -e .")
        print("  pytest tests/ -v")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)