#!/usr/bin/env python3
"""
Script to automatically update package versions in conda-sdk-client.yml by checking PyPI.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request
import json


def get_latest_pypi_version(package_name: str) -> str | None:
    """Get the latest version of a package from PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception as e:
        print(f" ⚠️  Error fetching {package_name}: {e}", file=sys.stderr)
        return None


def extract_packages_from_yaml(file_path: Path) -> List[Tuple[str, str, int]]:
    """
    Extract package names, versions, and line numbers from the YAML file.
    Returns list of tuples: (package_name, current_version, line_number)
    """
    packages = []
    content = file_path.read_text()
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for package: <name> lines (with or without leading dash)
        package_match = re.search(r'^\s*-?\s*package:\s+([a-z0-9\-_]+)\s*$', line)
        if package_match:
            package_name = package_match.group(1)
            # Look for the version on the next line
            if i + 1 < len(lines):
                version_match = re.search(r'^\s+version:\s+([0-9]+\.[0-9]+\.[0-9]+[a-z0-9]*)\s*$', lines[i + 1])
                if version_match:
                    version = version_match.group(1)
                    packages.append((package_name, version, i + 2))  # +2 for version line (1-based)
        i += 1
    
    return packages


def compare_versions(current: str, latest: str) -> bool:
    """
    Compare versions to determine if an update is needed.
    Returns True if latest > current.
    """
    def parse_version(v: str) -> Tuple:
        # Split into numeric and suffix parts
        parts = re.match(r'^(\d+)\.(\d+)\.(\d+)(.*)$', v)
        if parts:
            major, minor, patch, suffix = parts.groups()
            return (int(major), int(minor), int(patch), suffix or '')
        return (0, 0, 0, v)
    
    return parse_version(latest) > parse_version(current)


def update_yaml_file(file_path: Path, updates: Dict[int, str]) -> None:
    """
    Update the YAML file with new versions.
    updates: dict mapping line_number -> new_version
    """
    lines = file_path.read_text().split('\n')
    
    for line_num, new_version in updates.items():
        line_idx = line_num - 1  # Convert to 0-based index
        if line_idx < len(lines):
            # Replace the version while preserving indentation
            lines[line_idx] = re.sub(
                r'(^\s+version:\s+)[0-9]+\.[0-9]+\.[0-9]+[a-z0-9]*',
                rf'\g<1>{new_version}',
                lines[line_idx]
            )
    
    file_path.write_text('\n'.join(lines))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update package versions in conda-sdk-client.yml from PyPI')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--file', type=str, help='Path to YAML file (default: auto-detect)')
    args = parser.parse_args()
    
    if args.file:
        yaml_file = Path(args.file)
    else:
        yaml_file = Path(__file__).parent.parent / "eng" / "pipelines" / "templates" / "stages" / "conda-sdk-client.yml"
    
    if not yaml_file.exists():
        print(f"❌ Error: {yaml_file} not found")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    print(f"📋 Checking packages in {yaml_file.name}...\n")
    
    # Extract all packages
    packages = extract_packages_from_yaml(yaml_file)
    print(f"Found {len(packages)} packages to check\n")
    
    if not packages:
        print("⚠️  No packages found in the file!")
        sys.exit(1)
    
    # Check each package and collect updates
    updates = {}
    summary = {
        'checked': 0,
        'updated': 0,
        'current': 0,
        'errors': 0
    }
    
    for package_name, current_version, line_num in packages:
        summary['checked'] += 1
        print(f"Checking {package_name} (current: {current_version})...", end=' ')
        
        latest_version = get_latest_pypi_version(package_name)
        
        if latest_version is None:
            print("❌ Error")
            summary['errors'] += 1
            continue
        
        if latest_version == current_version:
            print(f"✅ Up to date")
            summary['current'] += 1
        elif compare_versions(current_version, latest_version):
            print(f"🔄 Update available: {current_version} -> {latest_version}")
            updates[line_num] = latest_version
            summary['updated'] += 1
        else:
            print(f"ℹ️  Current version ({current_version}) is newer than PyPI ({latest_version})")
            summary['current'] += 1
    
    # Apply updates if any
    if updates:
        if args.dry_run:
            print(f"\n🔍 Would update {len(updates)} package(s) in {yaml_file.name} (dry run)")
        else:
            print(f"\n📝 Updating {len(updates)} package(s) in {yaml_file.name}...")
            update_yaml_file(yaml_file, updates)
            print("✅ File updated successfully!")
    else:
        print("\n✅ All packages are up to date!")
    
    # Print summary
    print("\n" + "="*60)
    print("Summary:")
    print(f"  Total packages checked: {summary['checked']}")
    print(f"  Already up to date:     {summary['current']}")
    print(f"  Updated:                {summary['updated']}")
    print(f"  Errors:                 {summary['errors']}")
    print("="*60)


if __name__ == "__main__":
    main()
