#!/usr/bin/env python3
"""
Analyze operations that are unique to specific API versions or appear in only a subset of versions.
This helps identify new features introduced in specific API versions.
"""

import os
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def extract_operations_by_version():
    """Extract all operations organized by API version."""
    base_path = Path("azure/ai/ml/_restclient")
    version_operations = {}
    
    if not base_path.exists():
        print(f"❌ Path {base_path} does not exist")
        return {}
    
    # Get all version directories
    version_dirs = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    version_dirs.sort()
    
    for version_dir in version_dirs:
        operations_dir = version_dir / "operations"
        if not operations_dir.exists():
            continue
            
        version_name = version_dir.name
        operations = []
        
        # Find all operation files
        for op_file in operations_dir.glob("*_operations.py"):
            if op_file.name.startswith('_') and op_file.name.endswith('_operations.py'):
                # Extract operation name (remove leading _ and trailing _operations.py)
                op_name = op_file.name[1:-14]  # Remove '_' prefix and '_operations.py' suffix
                operations.append(op_name)
        
        version_operations[version_name] = sorted(operations)
    
    return version_operations

def analyze_operation_distribution(version_operations):
    """Analyze which operations appear in which versions."""
    # Count how many versions each operation appears in
    operation_counts = defaultdict(list)
    
    for version, operations in version_operations.items():
        for operation in operations:
            operation_counts[operation].append(version)
    
    return operation_counts

def categorize_operations(operation_counts, total_versions):
    """Categorize operations by their distribution across versions."""
    universal_ops = {}  # In all versions
    majority_ops = {}   # In >75% of versions
    subset_ops = {}     # In 25-75% of versions
    rare_ops = {}       # In <25% of versions
    unique_ops = {}     # In only 1 version
    
    for operation, versions in operation_counts.items():
        version_count = len(versions)
        percentage = (version_count / total_versions) * 100
        
        if version_count == total_versions:
            universal_ops[operation] = versions
        elif percentage > 75:
            majority_ops[operation] = versions
        elif percentage >= 25:
            subset_ops[operation] = versions
        elif version_count > 1:
            rare_ops[operation] = versions
        else:
            unique_ops[operation] = versions
    
    return universal_ops, majority_ops, subset_ops, rare_ops, unique_ops

def find_version_specific_introductions(version_operations, operation_counts):
    """Find when each operation was first introduced."""
    # Sort versions chronologically
    def version_sort_key(version):
        # Extract date components for sorting
        if 'dataplanepreview' in version:
            return (0, version)  # Put dataplanepreview first
        
        # Extract year, month, day for proper chronological sorting
        date_match = re.search(r'v(\d{4})_(\d{2})_(\d{2})', version)
        if date_match:
            year, month, day = map(int, date_match.groups())
            preview = 1 if 'preview' in version else 0
            return (1, year, month, day, preview)
        return (2, version)
    
    sorted_versions = sorted(version_operations.keys(), key=version_sort_key)
    
    operation_introductions = {}
    
    for operation, versions in operation_counts.items():
        # Find the earliest version where this operation appears
        earliest_version = None
        for version in sorted_versions:
            if version in versions:
                earliest_version = version
                break
        
        if earliest_version:
            operation_introductions[operation] = {
                'first_appeared': earliest_version,
                'total_versions': len(versions),
                'all_versions': sorted([v for v in versions], key=version_sort_key)
            }
    
    return operation_introductions, sorted_versions

def main():
    print("🔍 ANALYZING VERSION-SPECIFIC OPERATIONS")
    print("=" * 80)
    
    # Extract operations by version
    version_operations = extract_operations_by_version()
    
    if not version_operations:
        print("❌ No version operations found")
        return
    
    total_versions = len(version_operations)
    print(f"📊 Found {total_versions} API versions")
    
    # Show version summary
    print(f"\n📂 API Versions analyzed:")
    for version, ops in version_operations.items():
        print(f"  • {version}: {len(ops)} operations")
    
    # Analyze operation distribution
    operation_counts = analyze_operation_distribution(version_operations)
    total_operations = len(operation_counts)
    
    print(f"\n📊 Total unique operations found: {total_operations}")
    
    # Categorize operations
    universal_ops, majority_ops, subset_ops, rare_ops, unique_ops = categorize_operations(operation_counts, total_versions)
    
    print(f"\n🎯 OPERATION DISTRIBUTION ANALYSIS:")
    print("=" * 60)
    print(f"🌟 Universal operations (100%): {len(universal_ops)}")
    print(f"🔵 Majority operations (>75%): {len(majority_ops)}")
    print(f"🟡 Subset operations (25-75%): {len(subset_ops)}")
    print(f"🟠 Rare operations (<25%): {len(rare_ops)}")
    print(f"🔴 Unique operations (1 version): {len(unique_ops)}")
    
    # Find version-specific introductions
    operation_introductions, sorted_versions = find_version_specific_introductions(version_operations, operation_counts)
    
    # Show unique operations (most interesting for version-specific features)
    if unique_ops:
        print(f"\n🔴 UNIQUE OPERATIONS (Version-Specific Features):")
        print("=" * 60)
        for operation, versions in unique_ops.items():
            version = versions[0]
            print(f"  🚀 {operation}")
            print(f"     📅 Only in: {version}")
    
    # Show rare operations (introduced late or experimental)
    if rare_ops:
        print(f"\n🟠 RARE OPERATIONS (Limited Availability):")
        print("=" * 60)
        for operation, versions in sorted(rare_ops.items(), key=lambda x: len(x[1])):
            percentage = (len(versions) / total_versions) * 100
            intro_info = operation_introductions.get(operation, {})
            first_version = intro_info.get('first_appeared', 'Unknown')
            print(f"  🔸 {operation}")
            print(f"     📊 Available in: {len(versions)}/{total_versions} versions ({percentage:.1f}%)")
            print(f"     📅 First appeared: {first_version}")
            print(f"     📂 Versions: {', '.join(sorted(versions, key=lambda x: version_sort_key(x)))}")
            print()
    
    # Show subset operations (gradual rollout)
    if subset_ops:
        print(f"\n🟡 SUBSET OPERATIONS (Gradual Rollout):")
        print("=" * 60)
        for operation, versions in sorted(subset_ops.items(), key=lambda x: len(x[1]), reverse=True):
            percentage = (len(versions) / total_versions) * 100
            intro_info = operation_introductions.get(operation, {})
            first_version = intro_info.get('first_appeared', 'Unknown')
            print(f"  🔹 {operation}")
            print(f"     📊 Available in: {len(versions)}/{total_versions} versions ({percentage:.1f}%)")
            print(f"     📅 First appeared: {first_version}")
    
    # Analyze introduction timeline
    print(f"\n📈 FEATURE INTRODUCTION TIMELINE:")
    print("=" * 60)
    
    version_new_features = defaultdict(list)
    
    for operation, info in operation_introductions.items():
        first_version = info['first_appeared']
        total_count = info['total_versions']
        
        # Only show operations that are not universal (interesting new features)
        if total_count < total_versions:
            version_new_features[first_version].append((operation, total_count))
    
    for version in sorted_versions:
        if version in version_new_features:
            features = version_new_features[version]
            print(f"\n📅 {version}:")
            for operation, count in sorted(features, key=lambda x: x[1]):
                percentage = (count / total_versions) * 100
                status = "🔴 Unique" if count == 1 else f"🟠 Rare ({percentage:.1f}%)" if percentage < 25 else f"🟡 Subset ({percentage:.1f}%)"
                print(f"     🆕 {operation} - {status}")

def version_sort_key(version):
    """Sort versions chronologically."""
    if 'dataplanepreview' in version:
        return (0, version)
    
    date_match = re.search(r'v(\d{4})_(\d{2})_(\d{2})', version)
    if date_match:
        year, month, day = map(int, date_match.groups())
        preview = 1 if 'preview' in version else 0
        return (1, year, month, day, preview)
    return (2, version)

if __name__ == "__main__":
    main()