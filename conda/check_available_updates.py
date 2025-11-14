#!/usr/bin/env python3
"""Check which packages in conda-sdk-client.yml could be updated to newer PyPI versions."""

import re
import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional

def get_latest_pypi_version(package_name: str) -> Optional[str]:
    """Get the latest version of a package from PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception:
        return None

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

def compare_versions(current: str, latest: str) -> bool:
    """Returns True if latest > current."""
    def parse_version(v: str) -> tuple:
        parts = re.match(r'^(\d+)\.(\d+)\.(\d+)(.*)$', v)
        if parts:
            major, minor, patch, suffix = parts.groups()
            return (int(major), int(minor), int(patch), suffix or '')
        return (0, 0, 0, v)
    
    return parse_version(latest) > parse_version(current)

def main():
    yaml_file = Path(__file__).parent.parent / "eng" / "pipelines" / "templates" / "stages" / "conda-sdk-client.yml"
    
    print("📋 Checking packages in conda-sdk-client.yml against PyPI...\n")
    
    yaml_versions = extract_versions_from_yaml(yaml_file)
    print(f"Found {len(yaml_versions)} packages in YAML\n")
    
    updates_available = []
    up_to_date = 0
    errors = 0
    
    for pkg_name, current_version in sorted(yaml_versions.items()):
        print(f"Checking {pkg_name} (current: {current_version})...", end=' ')
        
        latest_version = get_latest_pypi_version(pkg_name)
        
        if latest_version is None:
            print("❌ Error fetching from PyPI")
            errors += 1
        elif latest_version == current_version:
            print("✅ Up to date")
            up_to_date += 1
        elif compare_versions(current_version, latest_version):
            print(f"🔄 Update available: {current_version} -> {latest_version}")
            updates_available.append((pkg_name, current_version, latest_version))
        else:
            print(f"ℹ️  YAML version ({current_version}) is newer than PyPI ({latest_version})")
            up_to_date += 1
    
    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  Total packages:      {len(yaml_versions)}")
    print(f"  Up to date:          {up_to_date}")
    print(f"  Updates available:   {len(updates_available)}")
    print(f"  Errors:              {errors}")
    print("="*70)
    
    if updates_available:
        print("\n📦 Packages with updates available:\n")
        for pkg, curr, latest in updates_available:
            print(f"  • {pkg}: {curr} → {latest}")

if __name__ == "__main__":
    main()
