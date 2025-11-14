#!/usr/bin/env python3
"""Sync release log versions to match conda-sdk-client.yml (the source of truth)."""

import re
from pathlib import Path
from typing import Dict

def extract_versions_from_yaml(yaml_file: Path) -> Dict[str, str]:
    """Extract package versions from conda-sdk-client.yml"""
    content = yaml_file.read_text()
    versions = {}
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        package_match = re.search(r'^\s*-?\s*package:\s+([a-z0-9\-_]+)\s*$', line)
        if package_match and i + 1 < len(lines):
            package_name = package_match.group(1)
            version_match = re.search(r'^\s+version:\s+([0-9]+\.[0-9]+\.[0-9]+[a-z0-9]*)\s*$', lines[i + 1])
            if version_match:
                versions[package_name] = version_match.group(1)
    
    return versions

def update_release_log(log_file: Path, yaml_versions: Dict[str, str]) -> bool:
    """Update a release log file to match YAML versions."""
    content = log_file.read_text()
    lines = content.split('\n')
    
    modified = False
    new_lines = []
    in_december = False
    in_packages = False
    
    for line in lines:
        if '## 2025.12.01' in line:
            in_december = True
            new_lines.append(line)
        elif line.startswith('## ') and in_december:
            in_december = False
            in_packages = False
            new_lines.append(line)
        elif in_december and '### Packages included' in line:
            in_packages = True
            new_lines.append(line)
        elif in_december and line.startswith('###'):
            in_packages = False
            new_lines.append(line)
        elif in_packages and line.strip().startswith('-'):
            match = re.search(r'-\s+([a-z0-9\-_]+)-(\d+\.\d+\.\d+[a-z0-9]*)', line)
            if match:
                pkg_name = match.group(1)
                old_version = match.group(2)
                
                if pkg_name in yaml_versions:
                    new_version = yaml_versions[pkg_name]
                    if old_version != new_version:
                        indent = len(line) - len(line.lstrip())
                        new_line = ' ' * indent + f"- {pkg_name}-{new_version}"
                        new_lines.append(new_line)
                        print(f"    {pkg_name}: {old_version} -> {new_version}")
                        modified = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        log_file.write_text('\n'.join(new_lines))
    
    return modified

def main():
    yaml_file = Path(__file__).parent.parent / "eng" / "pipelines" / "templates" / "stages" / "conda-sdk-client.yml"
    logs_dir = Path(__file__).parent / "conda-releaselogs"
    
    print("Reading versions from YAML (source of truth)...")
    yaml_versions = extract_versions_from_yaml(yaml_file)
    print(f"Found {len(yaml_versions)} packages in YAML\n")
    
    print("Updating release logs to match YAML versions...\n")
    
    modified_count = 0
    for log_file in sorted(logs_dir.glob("*.md")):
        print(f"Checking {log_file.name}...")
        if update_release_log(log_file, yaml_versions):
            modified_count += 1
    
    print(f"\n{'='*60}")
    print(f"Updated {modified_count} release log files")
    print("="*60)

if __name__ == "__main__":
    main()
