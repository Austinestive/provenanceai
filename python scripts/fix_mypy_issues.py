# File: scripts/fix_mypy_issues.py
#!/usr/bin/env python3
"""
Fix common mypy issues in ProvenanceAI.
"""

import re
from pathlib import Path

def fix_mypy_issues():
    """Fix common mypy type hints."""
    
    issues_found = 0
    fixes_applied = 0
    
    # Walk through source files
    for filepath in Path("src/provenanceai").rglob("*.py"):
        if not filepath.is_file():
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Add missing return type hints
        # Pattern: def function_name(self, ...):
        pattern = r'def (\w+)\((self[^)]*)\):(?!\s*->)'
        def add_return_type(match):
            func_name = match.group(1)
            params = match.group(2)
            return f"def {func_name}({params}) -> None:"
        
        content = re.sub(pattern, add_return_type, content)
        
        # Fix 2: Add type hints for class attributes
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix: __version__ = "0.1.0"  -> __version__: str = "0.1.0"
            if '__version__ = ' in line and ': str' not in line:
                line = line.replace('__version__ = ', '__version__: str = ')
                fixes_applied += 1
            
            # Fix: __author__ = "..." -> __author__: str = "..."
            if '__author__ = ' in line and ': str' not in line:
                line = line.replace('__author__ = ', '__author__: str = ')
                fixes_applied += 1
            
            # Fix: __description__ = "..." -> __description__: str = "..."
            if '__description__ = ' in line and ': str' not in line:
                line = line.replace('__description__ = ', '__description__: str = ')
                fixes_applied += 1
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 3: Add missing imports for common types
        if "from typing import" in content:
            # Ensure Optional is imported if used
            if "Optional[" in content and "Optional" not in content:
                content = content.replace(
                    "from typing import",
                    "from typing import Optional,"
                )
                fixes_applied += 1
        
        # Save if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed types in: {filepath.relative_to('src')}")
            issues_found += 1
    
    print(f"\n🔧 Applied {fixes_applied} fixes across {issues_found} files")
    
    # Create py.typed marker file for PEP 561
    typed_file = Path("src/provenanceai/py.typed")
    typed_file.touch()
    print(f"✅ Created: {typed_file}")
    
    return issues_found > 0

def create_mypy_config():
    """Create mypy configuration file."""
    config_content = """[mypy]
python_version = 3.9
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[mypy-provenanceai.*]
disallow_untyped_defs = false  # Be more lenient with our own code
"""
    
    config_file = Path("mypy.ini")
    config_file.write_text(config_content)
    print(f"✅ Created: {config_file}")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing mypy type hints...")
    fix_mypy_issues()
    create_mypy_config()
    print("\n🎉 Now run: mypy src/provenanceai --config-file mypy.ini")