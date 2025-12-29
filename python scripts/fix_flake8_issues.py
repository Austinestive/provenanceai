# File: scripts/fix_flake8_issues.py
#!/usr/bin/env python3
"""
Fix common flake8 issues.
"""

from pathlib import Path
import re

def fix_flake8_issues():
    """Fix common flake8 warnings."""
    
    fixes = {
        'E302': 'expected 2 blank lines, found 1',
        'E305': 'expected 2 blank lines after class or function definition',
        'E501': 'line too long',
        'F401': 'module imported but unused',
        'F821': 'undefined name',
    }
    
    issues_found = 0
    
    for filepath in Path("src/provenanceai").rglob("*.py"):
        if not filepath.is_file():
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix E501: Line too long (limit to 88 chars for black compatibility)
            if len(line) > 88 and not line.strip().startswith(('#', '"', "'")):
                # Don't break URLs or long strings
                if 'http://' not in line and 'https://' not in line:
                    # Try to break at natural points
                    if 'def ' in line or 'class ' in line:
                        # Don't break function/class definitions
                        fixed_lines.append(line)
                    elif '(' in line and ')' in line:
                        # Try to break at commas in function calls
                        parts = []
                        current = ''
                        in_string = False
                        string_char = None
                        
                        for char in line:
                            if char in ('"', "'") and not in_string:
                                in_string = True
                                string_char = char
                            elif char == string_char and in_string:
                                in_string = False
                                string_char = None
                            
                            current += char
                            
                            if not in_string and char == ',' and len(current) > 40:
                                parts.append(current)
                                current = ''
                        
                        if current:
                            parts.append(current)
                        
                        if len(parts) > 1:
                            fixed_lines.append(parts[0])
                            for part in parts[1:]:
                                fixed_lines.append('    ' + part.strip())
                            issues_found += 1
                            continue
            
            # Fix F401: Remove unused imports (basic check)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Keep the import for now - we'll handle this differently
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix E302/E305: Ensure proper blank lines
        # Add blank lines after class/function definitions
        content = re.sub(r'(\nclass \w+.*:\n)(?!\n)', r'\1\n', content)
        content = re.sub(r'(\ndef \w+.*:\n)(?!\n)', r'\1\n', content)
        
        # Ensure 2 blank lines between top-level classes/functions
        content = re.sub(r'(\nclass \w+.*:\n\n)(\S)', r'\1\n\2', content)
        content = re.sub(r'(\ndef \w+.*:\n\n)(\S)', r'\1\n\2', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed formatting in: {filepath.relative_to('src')}")
            issues_found += 1
    
    print(f"\n🔧 Fixed issues in {issues_found} files")
    
    # Create .flake8 config
    config_content = """[flake8]
max-line-length = 88
extend-ignore = E203, W503  # Black compatibility
exclude = 
    .git,
    __pycache__,
    .pytest_cache,
    .venv,
    venv,
    dist,
    build
"""
    
    config_file = Path(".flake8")
    config_file.write_text(config_content)
    print(f"✅ Created: {config_file}")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing flake8 issues...")
    fix_flake8_issues()
    print("\n🎉 Now run: flake8 src/provenanceai")