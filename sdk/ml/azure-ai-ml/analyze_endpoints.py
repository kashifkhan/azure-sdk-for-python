#!/usr/bin/env python3
"""
Analyze _restclient endpoints and configurations.
This script analyzes the actual endpoints and service URLs to understand
if different API versions are for the same or different services.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_endpoints():
    # Base paths
    restclient_path = Path("/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/_restclient")
    
    print("🔍 Analyzing _restclient endpoints and configurations...")
    print("=" * 70)
    
    # Get actual folders
    actual_folders = []
    if restclient_path.exists():
        for item in restclient_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
                actual_folders.append(item.name)
    
    print(f"📁 Found {len(actual_folders)} folders in _restclient:")
    for folder in sorted(actual_folders):
        print(f"  - {folder}")
    
    print(f"\n🔍 ANALYZING CONFIGURATION FILES:")
    print("=" * 70)
    
    endpoint_info = defaultdict(dict)
    
    for folder in sorted(actual_folders):
        folder_path = restclient_path / folder
        print(f"\n📂 {folder}:")
        
        # Look for configuration files
        config_files = [
            "_configuration.py",
            "__init__.py", 
            "_azure_machine_learning_workspaces.py",
            "_version.py"
        ]
        
        found_configs = []
        for config_file in config_files:
            config_path = folder_path / config_file
            if config_path.exists():
                found_configs.append(config_file)
        
        if found_configs:
            print(f"  📄 Config files: {', '.join(found_configs)}")
            
            # Analyze configuration file
            config_path = folder_path / "_configuration.py"
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding='utf-8')
                    
                    # Look for base URL patterns
                    base_url_match = re.search(r'DEFAULT_API_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                    if base_url_match:
                        endpoint_info[folder]['api_version'] = base_url_match.group(1)
                    
                    # Look for service names
                    service_match = re.search(r'class\s+(\w+Configuration)', content)
                    if service_match:
                        endpoint_info[folder]['service_class'] = service_match.group(1)
                    
                    # Look for any hardcoded URLs or endpoints
                    url_patterns = re.findall(r'https?://[^\s\'"]+', content)
                    if url_patterns:
                        endpoint_info[folder]['urls'] = url_patterns
                    
                    # Look for API version patterns
                    api_patterns = re.findall(r'["\'](\d{4}-\d{2}-\d{2}[^"\']*)["\']', content)
                    if api_patterns:
                        endpoint_info[folder]['api_patterns'] = list(set(api_patterns))
                    
                    print(f"    📋 API Version: {endpoint_info[folder].get('api_version', 'Not found')}")
                    print(f"    🏗️  Service Class: {endpoint_info[folder].get('service_class', 'Not found')}")
                    if endpoint_info[folder].get('urls'):
                        print(f"    🌐 URLs: {endpoint_info[folder]['urls']}")
                    if endpoint_info[folder].get('api_patterns'):
                        print(f"    📅 API Patterns: {endpoint_info[folder]['api_patterns']}")
                        
                except Exception as e:
                    print(f"    ⚠️  Error reading config: {e}")
            
            # Check the main client file
            client_files = list(folder_path.glob("_azure_machine_learning*.py"))
            if client_files:
                client_file = client_files[0]
                try:
                    content = client_file.read_text(encoding='utf-8')
                    
                    # Look for service class definitions
                    class_match = re.search(r'class\s+(\w+)\([^)]*\):', content)
                    if class_match:
                        endpoint_info[folder]['client_class'] = class_match.group(1)
                    
                    # Look for base URL construction
                    base_url_matches = re.findall(r'self\._base_url\s*=\s*["\']([^"\']+)["\']', content)
                    if base_url_matches:
                        endpoint_info[folder]['base_url'] = base_url_matches[0]
                    
                    print(f"    🏢 Client Class: {endpoint_info[folder].get('client_class', 'Not found')}")
                    print(f"    🔗 Base URL: {endpoint_info[folder].get('base_url', 'Not found')}")
                    
                except Exception as e:
                    print(f"    ⚠️  Error reading client: {e}")
        else:
            print(f"  ⚠️  No standard config files found")
    
    print(f"\n📊 ENDPOINT ANALYSIS:")
    print("=" * 70)
    
    # Group by service patterns
    service_groups = defaultdict(list)
    client_groups = defaultdict(list)
    
    for folder, info in endpoint_info.items():
        service_class = info.get('service_class', 'Unknown')
        client_class = info.get('client_class', 'Unknown')
        
        service_groups[service_class].append(folder)
        client_groups[client_class].append(folder)
    
    print(f"🏗️  SERVICE CONFIGURATIONS:")
    for service, folders in service_groups.items():
        print(f"  {service}: {len(folders)} folders")
        for folder in sorted(folders):
            api_ver = endpoint_info[folder].get('api_version', 'N/A')
            print(f"    - {folder} (API: {api_ver})")
    
    print(f"\n🏢 CLIENT CLASSES:")
    for client, folders in client_groups.items():
        print(f"  {client}: {len(folders)} folders")
        for folder in sorted(folders):
            base_url = endpoint_info[folder].get('base_url', 'N/A')
            print(f"    - {folder} (Base URL: {base_url})")
    
    # Check for patterns in folder names
    print(f"\n🔍 FOLDER NAME PATTERNS:")
    print("=" * 70)
    
    version_patterns = defaultdict(list)
    for folder in actual_folders:
        if 'v20' in folder:  # Version pattern
            # Extract the version part
            version_match = re.search(r'v(\d{4}_\d{2}_\d{2})', folder)
            if version_match:
                version = version_match.group(1)
                suffix = folder.replace(f'v{version}', '').strip('_')
                pattern = f"v{version}" + (f"_{suffix}" if suffix else "")
                version_patterns[suffix or 'stable'].append(pattern)
        else:
            version_patterns['other'].append(folder)
    
    for pattern_type, versions in version_patterns.items():
        print(f"  {pattern_type}: {len(versions)} versions")
        for version in sorted(versions):
            print(f"    - {version}")
    
    print(f"\n🎯 CONCLUSION:")
    print("=" * 70)
    
    unique_services = len([s for s in service_groups.keys() if s != 'Unknown'])
    unique_clients = len([c for c in client_groups.keys() if c != 'Unknown'])
    
    print(f"  • Unique service configurations: {unique_services}")
    print(f"  • Unique client classes: {unique_clients}")
    print(f"  • Total API versions: {len(actual_folders)}")
    
    # Check if they're likely the same service
    if unique_clients <= 2 and any('AzureMachineLearning' in client for client in client_groups.keys()):
        print(f"  • Assessment: Likely SAME SERVICE with different API versions")
    else:
        print(f"  • Assessment: Possibly DIFFERENT SERVICES or mixed")

if __name__ == "__main__":
    analyze_endpoints()