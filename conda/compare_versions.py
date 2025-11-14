#!/usr/bin/env python3
"""Compare versions between conda-sdk-client.yml and release logs."""

import re
from pathlib import Path
from typing import Dict

def extract_versions_from_yaml(yaml_file: Path) -> Dict[str, str]:
    """Extract package versions from conda-sdk-client.yml"""
    content = yaml_file.read_text()
    versions = {}
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Match package: name pattern
        package_match = re.search(r'^\s*-?\s*package:\s+([a-z0-9\-_]+)\s*$', line)
        if package_match and i + 1 < len(lines):
            package_name = package_match.group(1)
            # Check next line for version
            version_match = re.search(r'^\s+version:\s+([0-9]+\.[0-9]+\.[0-9]+[a-z0-9]*)\s*$', lines[i + 1])
            if version_match:
                versions[package_name] = version_match.group(1)
    
    return versions

def extract_versions_from_release_logs(logs_dir: Path) -> Dict[str, str]:
    """Extract versions from the latest (2025.12.01) sections in release logs"""
    versions = {}
    
    for md_file in logs_dir.glob("*.md"):
        content = md_file.read_text()
        lines = content.split('\n')
        
        in_december_section = False
        in_packages = False
        
        for line in lines:
            if '## 2025.12.01' in line:
                in_december_section = True
                continue
            elif line.startswith('## ') and in_december_section:
                break
            
            if in_december_section and '### Packages included' in line:
                in_packages = True
                continue
            elif in_december_section and line.startswith('###'):
                in_packages = False
            
            if in_packages and line.strip().startswith('-'):
                match = re.search(r'-\s+([a-z0-9\-_]+)-(\d+\.\d+\.\d+[a-z0-9]*)', line)
                if match:
                    versions[match.group(1)] = match.group(2)
    
    return versions

def main():
    yaml_file = Path(__file__).parent.parent / "eng" / "pipelines" / "templates" / "stages" / "conda-sdk-client.yml"
    logs_dir = Path(__file__).parent / "conda-releaselogs"
    
    yaml_versions = extract_versions_from_yaml(yaml_file)
    log_versions = extract_versions_from_release_logs(logs_dir)
    
    print(f"Found {len(yaml_versions)} packages in YAML")
    print(f"Found {len(log_versions)} packages in release logs")
    print()
    
    mismatches = []
    missing_in_logs = []
    missing_in_yaml = []
    
    # Check YAML packages against logs
    for pkg, yaml_ver in sorted(yaml_versions.items()):
        if pkg in log_versions:
            log_ver = log_versions[pkg]
            if yaml_ver != log_ver:
                mismatches.append((pkg, yaml_ver, log_ver))
        else:
            missing_in_logs.append((pkg, yaml_ver))
    
    # Check log packages not in YAML
    for pkg in sorted(log_versions.keys()):
        if pkg not in yaml_versions:
            missing_in_yaml.append((pkg, log_versions[pkg]))
    
    if mismatches:
        print("❌ VERSION MISMATCHES:")
        print("-" * 80)
        for pkg, yaml_ver, log_ver in mismatches:
            print(f"  {pkg}:")
            print(f"    YAML: {yaml_ver}")
            print(f"    LOG:  {log_ver}")
        print()
    
    if missing_in_logs:
        print("⚠️  PACKAGES IN YAML BUT NOT IN RELEASE LOGS:")
        print("-" * 80)
        for pkg, ver in missing_in_logs:
            print(f"  {pkg}: {ver}")
        print()
    
    if missing_in_yaml:
        print("⚠️  PACKAGES IN RELEASE LOGS BUT NOT IN YAML:")
        print("-" * 80)
        for pkg, ver in missing_in_yaml:
            print(f"  {pkg}: {ver}")
        print()
    
    if not mismatches and not missing_in_logs and not missing_in_yaml:
        print("✅ ALL VERSIONS MATCH PERFECTLY!")
    else:
        print("=" * 80)
        print(f"Summary:")
        print(f"  Mismatches: {len(mismatches)}")
        print(f"  Missing in logs: {len(missing_in_logs)}")
        print(f"  Missing in YAML: {len(missing_in_yaml)}")

if __name__ == "__main__":
    main()
