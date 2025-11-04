#!/usr/bin/env python3
"""
Analyze _restclient import patterns.
This script analyzes what specifically is being imported from _restclient folders.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_import_patterns():
    # Base paths
    restclient_path = Path("/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/_restclient")
    sdk_path = Path("/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml")
    
    print("🔍 Analyzing _restclient import patterns...")
    print("=" * 60)
    
    # Different patterns to capture various import styles
    patterns = {
        'models_import': r'from azure\.ai\.ml\._restclient\.([^.\s]+)\.models import',
        'direct_client': r'from azure\.ai\.ml\._restclient\.([^.\s]+) import (\w+)',
        'operations_import': r'from azure\.ai\.ml\._restclient\.([^.\s]+)\.operations import',
        'full_import': r'from azure\.ai\.ml\._restclient\.([^.\s]+)(?:\.([^.\s]+))? import ([^#\n]+)',
    }
    
    import_patterns = defaultdict(list)
    folder_usage = defaultdict(set)
    import_types = Counter()
    
    # Search through all Python files
    python_files = list(sdk_path.rglob("*.py"))
    print(f"🔎 Searching through {len(python_files)} Python files...")
    
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if 'from azure.ai.ml._restclient.' in line and 'import' in line:
                    line_clean = line.strip()
                    
                    # Check each pattern
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, line_clean)
                        if matches:
                            for match in matches:
                                if pattern_name == 'full_import':
                                    folder, submodule, imports = match
                                    folder_usage[folder].add(f"{submodule or 'direct'}")
                                    import_patterns[folder].append({
                                        'file': str(py_file.relative_to(sdk_path)),
                                        'line': i,
                                        'content': line_clean,
                                        'pattern': pattern_name,
                                        'submodule': submodule or 'direct',
                                        'imports': imports.strip()
                                    })
                                    
                                    # Count import types
                                    if '.models' in line_clean:
                                        import_types['models'] += 1
                                    elif '.operations' in line_clean:
                                        import_types['operations'] += 1
                                    elif submodule == '':
                                        import_types['client_direct'] += 1
                                    else:
                                        import_types['other'] += 1
                                else:
                                    if isinstance(match, tuple):
                                        folder = match[0]
                                    else:
                                        folder = match
                                    
                                    folder_usage[folder].add(pattern_name)
                                    import_patterns[folder].append({
                                        'file': str(py_file.relative_to(sdk_path)),
                                        'line': i,
                                        'content': line_clean,
                                        'pattern': pattern_name
                                    })
                                    
                                    # Count import types
                                    import_types[pattern_name] += 1
                            
        except (OSError, UnicodeDecodeError) as e:
            print(f"⚠️  Error reading {py_file}: {e}")
            continue
    
    print(f"📊 IMPORT TYPE ANALYSIS:")
    print("=" * 60)
    print(f"Total import statements found: {sum(import_types.values())}")
    print()
    
    for import_type, count in import_types.most_common():
        percentage = (count / sum(import_types.values())) * 100
        print(f"  {import_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n📦 FOLDER USAGE PATTERNS:")
    print("=" * 60)
    
    for folder in sorted(folder_usage.keys()):
        imports = import_patterns[folder]
        print(f"\n🔸 {folder} ({len(imports)} imports):")
        
        # Group by submodule type
        submodule_counts = Counter()
        sample_imports = defaultdict(list)
        
        for imp in imports:
            submodule = imp.get('submodule', imp.get('pattern', 'unknown'))
            submodule_counts[submodule] += 1
            if len(sample_imports[submodule]) < 3:  # Keep first 3 samples
                sample_imports[submodule].append(imp['content'])
        
        for submodule, count in submodule_counts.most_common():
            print(f"  📁 {submodule}: {count} imports")
            for sample in sample_imports[submodule]:
                print(f"    → {sample}")
            if len(sample_imports[submodule]) == 3 and count > 3:
                print(f"    ... and {count - 3} more")
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 60)
    print(f"  • Total folders with imports: {len(folder_usage)}")
    print(f"  • Total import statements: {sum(import_types.values())}")
    
    models_count = import_types.get('models', 0) + sum(1 for imp_list in import_patterns.values() for imp in imp_list if '.models' in imp['content'])
    client_count = import_types.get('client_direct', 0) + sum(1 for imp_list in import_patterns.values() for imp in imp_list if '.models' not in imp['content'] and '.operations' not in imp['content'])
    operations_count = import_types.get('operations', 0) + sum(1 for imp_list in import_patterns.values() for imp in imp_list if '.operations' in imp['content'])
    
    print(f"  • Imports from .models: ~{models_count}")
    print(f"  • Imports from .operations: ~{operations_count}") 
    print(f"  • Direct client imports: ~{client_count}")
    
    # Answer the specific question
    print(f"\n❓ ANSWER TO YOUR QUESTION:")
    print("=" * 60)
    
    total_imports = sum(len(imports) for imports in import_patterns.values())
    models_imports = sum(1 for imp_list in import_patterns.values() for imp in imp_list if '.models' in imp['content'])
    non_models_imports = total_imports - models_imports
    
    print(f"  • Total imports: {total_imports}")
    print(f"  • Imports with '.models': {models_imports} ({(models_imports/total_imports)*100:.1f}%)")
    print(f"  • Imports WITHOUT '.models': {non_models_imports} ({(non_models_imports/total_imports)*100:.1f}%)")
    
    if non_models_imports > 0:
        print(f"\n  📋 Examples of imports WITHOUT '.models':")
        count = 0
        for imp_list in import_patterns.values():
            for imp in imp_list:
                if '.models' not in imp['content'] and count < 10:
                    print(f"    → {imp['content']}")
                    count += 1
                if count >= 10:
                    break
            if count >= 10:
                break
    
    # NEW SECTION: Comprehensive import pattern breakdown
    print("\n📋 COMPREHENSIVE IMPORT PATTERN BREAKDOWN:")
    print("=" * 60)
    
    # Collect all unique import patterns
    all_patterns = defaultdict(set)
    
    for imp_list in import_patterns.values():
        for imp in imp_list:
            content = imp['content']
            
            # Extract the pattern after _restclient
            match = re.search(r'from azure\.ai\.ml\._restclient\.([^.\s]+)(?:\.([^.\s]+))?(?:\.([^.\s]+))? import', content)
            if match:
                folder, submodule1, submodule2 = match.groups()
                
                if submodule2:  # e.g., _restclient.v2022_10_01.models._models_py3
                    pattern = f"{submodule1}.{submodule2}"
                elif submodule1:  # e.g., _restclient.v2022_10_01.models
                    pattern = submodule1
                else:  # e.g., _restclient.v2022_10_01 (direct)
                    pattern = "direct"
                
                all_patterns[pattern].add(content)
    
    # Sort patterns and display
    for pattern in sorted(all_patterns.keys()):
        imports = all_patterns[pattern]
        print(f"\n🔹 Pattern: _restclient.*.{pattern} ({len(imports)} unique imports)")
        
        # Show up to 5 examples
        for i, import_line in enumerate(sorted(imports)):
            if i >= 5:
                print(f"    ... and {len(imports) - 5} more")
                break
            print(f"    → {import_line}")
    
    # Also show the distribution by pattern type
    print("\n📊 PATTERN DISTRIBUTION:")
    print("=" * 60)
    
    pattern_counts = Counter()
    for pattern, imports in all_patterns.items():
        pattern_counts[pattern] = len(imports)
    
    total_unique = sum(pattern_counts.values())
    for pattern, count in pattern_counts.most_common():
        percentage = (count / total_unique) * 100
        print(f"  {pattern}: {count} unique imports ({percentage:.1f}%)")

if __name__ == "__main__":
    analyze_import_patterns()