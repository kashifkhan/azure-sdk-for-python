#!/usr/bin/env python3
"""
Analyze ARM resource types and operations across different API versions.
This script checks if different API versions operate on the same resource types
and have the same operations.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_arm_operations():
    # Base paths
    restclient_path = Path("/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/_restclient")
    
    print("🔍 Analyzing ARM operations and resource types...")
    print("=" * 70)
    
    # Get version folders (exclude non-version folders)
    version_folders = []
    if restclient_path.exists():
        for item in restclient_path.iterdir():
            if item.is_dir() and item.name.startswith('v20') and not item.name.startswith('__'):
                version_folders.append(item.name)
    
    print(f"📁 Found {len(version_folders)} API version folders:")
    for folder in sorted(version_folders):
        print(f"  - {folder}")
    
    print(f"\n🔍 ANALYZING OPERATIONS FILES:")
    print("=" * 70)
    
    operations_by_version = defaultdict(dict)
    resource_types_by_version = defaultdict(set)
    
    for version in sorted(version_folders):
        version_path = restclient_path / version
        operations_dir = version_path / "operations"
        
        print(f"\n📂 {version}:")
        
        if not operations_dir.exists():
            print(f"  ⚠️  No operations directory found")
            continue
            
        # Get all operation files
        operation_files = list(operations_dir.glob("_*_operations.py"))
        if not operation_files:
            operation_files = list(operations_dir.glob("*.py"))
        
        print(f"  📄 Found {len(operation_files)} operation files:")
        
        for op_file in operation_files:
            op_name = op_file.stem.replace('_operations', '').replace('_', '')
            print(f"    - {op_file.name}")
            
            try:
                content = op_file.read_text(encoding='utf-8')
                
                # Look for ARM resource patterns in URLs
                # ARM URLs typically look like: /subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}
                arm_patterns = re.findall(r'/providers/([^/]+)/([^/\'"{\s]+)', content)
                
                # Look for resource type patterns
                resource_patterns = re.findall(r'Microsoft\.MachineLearningServices/(\w+)', content)
                
                # Look for method definitions to understand operations
                method_patterns = re.findall(r'def\s+(\w+)\s*\(', content)
                
                # Store findings
                if arm_patterns:
                    operations_by_version[version][op_name] = {
                        'file': op_file.name,
                        'arm_patterns': list(set(arm_patterns)),
                        'resource_patterns': list(set(resource_patterns)),
                        'methods': [m for m in method_patterns if not m.startswith('_')][:10]  # First 10 public methods
                    }
                    
                    # Extract resource types
                    for provider, resource_type in arm_patterns:
                        if 'MachineLearningServices' in provider:
                            resource_types_by_version[version].add(resource_type)
                
            except Exception as e:
                print(f"      ⚠️  Error reading {op_file.name}: {e}")
    
    print(f"\n📊 RESOURCE TYPE ANALYSIS:")
    print("=" * 70)
    
    # Analyze resource types across versions
    all_resource_types = set()
    for version, resources in resource_types_by_version.items():
        all_resource_types.update(resources)
    
    print(f"🏗️  All unique resource types found: {len(all_resource_types)}")
    for resource_type in sorted(all_resource_types):
        versions_with_resource = []
        for version, resources in resource_types_by_version.items():
            if resource_type in resources:
                versions_with_resource.append(version)
        
        print(f"  📦 {resource_type}: {len(versions_with_resource)} versions")
        if len(versions_with_resource) <= 5:
            print(f"      Versions: {', '.join(sorted(versions_with_resource))}")
        else:
            print(f"      Versions: {', '.join(sorted(versions_with_resource)[:3])} ... and {len(versions_with_resource)-3} more")
    
    print(f"\n🔧 OPERATIONS ANALYSIS:")
    print("=" * 70)
    
    # Analyze operations across versions
    all_operations = set()
    for version, ops in operations_by_version.items():
        all_operations.update(ops.keys())
    
    print(f"⚙️  All unique operation types found: {len(all_operations)}")
    
    for operation in sorted(all_operations):
        versions_with_op = []
        for version, ops in operations_by_version.items():
            if operation in ops:
                versions_with_op.append(version)
        
        print(f"\n  🔧 {operation}: {len(versions_with_op)} versions")
        
        if len(versions_with_op) <= 3:
            # Show details for operations in few versions
            for version in sorted(versions_with_op):
                op_info = operations_by_version[version][operation]
                print(f"    📂 {version}:")
                print(f"      📄 File: {op_info['file']}")
                if op_info['resource_patterns']:
                    print(f"      📦 Resources: {', '.join(op_info['resource_patterns'][:3])}")
                if op_info['methods']:
                    print(f"      ⚙️  Methods: {', '.join(op_info['methods'][:5])}")
        else:
            print(f"    Versions: {', '.join(sorted(versions_with_op)[:5])}...")
    
    print(f"\n🎯 ARM RESOURCE TYPE CONSISTENCY ANALYSIS:")
    print("=" * 70)
    
    # Check consistency of resource types across versions
    resource_consistency = defaultdict(list)
    
    for resource_type in all_resource_types:
        versions_with_resource = []
        for version, resources in resource_types_by_version.items():
            if resource_type in resources:
                versions_with_resource.append(version)
        
        if len(versions_with_resource) > 1:
            resource_consistency[resource_type] = versions_with_resource
    
    print(f"📋 Resource types shared across multiple API versions:")
    
    for resource_type, versions in sorted(resource_consistency.items()):
        percentage = (len(versions) / len(version_folders)) * 100
        print(f"  📦 {resource_type}: {len(versions)}/{len(version_folders)} versions ({percentage:.1f}%)")
        
        # Check if operations are similar across versions for this resource type
        common_methods = set()
        version_methods = {}
        
        for version in versions:
            for op_name, op_info in operations_by_version.get(version, {}).items():
                if resource_type in op_info.get('resource_patterns', []):
                    version_methods[version] = op_info['methods']
                    if not common_methods:
                        common_methods = set(op_info['methods'])
                    else:
                        common_methods &= set(op_info['methods'])
        
        if common_methods:
            print(f"    🔧 Common methods: {', '.join(sorted(list(common_methods)[:5]))}")
    
    print(f"\n🎯 CONCLUSION:")
    print("=" * 70)
    
    shared_resources = len(resource_consistency)
    total_resources = len(all_resource_types)
    consistency_ratio = (shared_resources / total_resources) * 100 if total_resources > 0 else 0
    
    print(f"  • Total unique resource types: {total_resources}")
    print(f"  • Resource types shared across versions: {shared_resources}")
    print(f"  • Consistency ratio: {consistency_ratio:.1f}%")
    print(f"  • Total API versions analyzed: {len(version_folders)}")
    
    if consistency_ratio > 70:
        print(f"  • Assessment: HIGH consistency - Same service with evolving API versions")
    elif consistency_ratio > 40:
        print(f"  • Assessment: MODERATE consistency - Mostly same service with some new features")
    else:
        print(f"  • Assessment: LOW consistency - Possibly different services or major changes")

if __name__ == "__main__":
    analyze_arm_operations()