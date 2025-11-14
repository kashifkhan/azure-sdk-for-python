#!/usr/bin/env python3
"""
Script to update conda release log files with new monthly sections.
Adds ## 2025.12.01 section if missing, using latest PyPI version or carrying over previous version.
"""

import re
import sys
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_latest_pypi_version(package_name: str) -> Optional[str]:
    """Get the latest version of a package from PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception as e:
        print(f"  ⚠️  Error fetching {package_name}: {e}", file=sys.stderr)
        return None


def extract_package_info_from_md(content: str, filename: str) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Extract package names and most recent versions from markdown content.
    Returns (base_package_name, {package_name: version})
    """
    # Extract base package name from filename (e.g., azure-ai-voicelive.md -> azure-ai-voicelive)
    base_package_name = filename.replace('.md', '')
    
    # Find all package entries in the first section (most recent)
    lines = content.split('\n')
    package_versions = {}
    in_packages_section = False
    
    for line in lines:
        # Look for "### Packages included" header
        if '### Packages included' in line:
            in_packages_section = True
            continue
        
        # Stop at next section header or another date header
        if in_packages_section and (line.startswith('###') or line.startswith('##')):
            break
        
        # Extract package entries
        if in_packages_section and line.strip().startswith('-'):
            # Match pattern: - package-name-version
            match = re.search(r'-\s+([a-z0-9\-_]+)-(\d+\.\d+\.\d+[a-z0-9]*)', line)
            if match:
                pkg_name = match.group(1)
                version = match.group(2)
                package_versions[pkg_name] = version
    
    return base_package_name, package_versions


def has_december_2025_section(content: str) -> bool:
    """Check if the file already has a ## 2025.12.01 section."""
    return '## 2025.12.01' in content


def get_package_entries_from_section(content: str, section_header: str) -> List[str]:
    """Extract package entries from a specific section."""
    lines = content.split('\n')
    entries = []
    in_section = False
    in_packages = False
    
    for line in lines:
        if line.startswith('## ') and section_header in line:
            in_section = True
            continue
        elif line.startswith('## ') and in_section:
            break
        
        if in_section:
            if '### Packages included' in line:
                in_packages = True
                continue
            elif line.startswith('###'):
                in_packages = False
            elif in_packages and line.strip().startswith('-'):
                entries.append(line.strip())
    
    return entries


def add_december_section(content: str, package_entries: List[str]) -> str:
    """Add a new ## 2025.12.01 section at the top of the file."""
    lines = content.split('\n')
    
    # Find the title line (first line, e.g., "Azure AI VoiceLive client library for Python (conda)")
    title_line = lines[0] if lines else ""
    
    # Create the package list
    packages_list = '\n'.join(f"- {entry}" for entry in package_entries)
    
    # Create the new section
    new_section = f"""## 2025.12.01

### Packages included

{packages_list}
"""
    
    # Insert after title and blank line
    if len(lines) > 1:
        # Insert after title
        result = [title_line, ""]
        result.append(new_section.strip())
        result.append("")
        result.extend(lines[2:] if len(lines) > 2 else [])
        return '\n'.join(result)
    else:
        return title_line + '\n\n' + new_section


def process_release_log(file_path: Path, pypi_versions: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Process a single release log file.
    Returns True if file would be/was modified, False otherwise.
    """
    content = file_path.read_text()
    filename = file_path.name
    
    # Check if already has December 2025 section
    if has_december_2025_section(content):
        print(f"  ✅ Already has 2025.12.01 section")
        return False
    
    # Extract package info (can be multiple packages)
    base_name, previous_packages = extract_package_info_from_md(content, filename)
    
    if not previous_packages:
        print(f"  ⚠️  Could not extract any packages")
        return False
    
    # Build list of package entries for the new section
    package_entries = []
    has_updates = False
    
    for pkg_name, prev_version in previous_packages.items():
        pypi_version = pypi_versions.get(pkg_name)
        
        if pypi_version and pypi_version != prev_version:
            # Update to new version
            package_entries.append(f"{pkg_name}-{pypi_version}")
            print(f"  🔄 {pkg_name}: {prev_version} -> {pypi_version}")
            has_updates = True
        else:
            # Carry over previous version
            package_entries.append(f"{pkg_name}-{prev_version}")
            if pypi_version:
                print(f"  ✅ {pkg_name}: {prev_version} (up to date)")
            else:
                print(f"  ♻️  {pkg_name}: {prev_version} (carried over)")
    
    if not package_entries:
        print(f"  ⚠️  No package entries to add")
        return False
    
    # Add new section
    if dry_run:
        print(f"  🔍 Would add 2025.12.01 section with {len(package_entries)} package(s)")
    else:
        new_content = add_december_section(content, package_entries)
        file_path.write_text(new_content)
        print(f"  ✅ Added 2025.12.01 section")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update conda release logs with December 2025 sections')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    args = parser.parse_args()
    
    releaselogs_dir = Path(__file__).parent / "conda-releaselogs"
    
    if not releaselogs_dir.exists():
        print(f"❌ Error: {releaselogs_dir} not found")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    # Get all markdown files
    md_files = sorted(releaselogs_dir.glob("*.md"))
    
    if not md_files:
        print(f"⚠️  No markdown files found in {releaselogs_dir}")
        sys.exit(1)
    
    print(f"📋 Found {len(md_files)} release log files\n")
    
    # First, collect all package names and get their PyPI versions
    print("🔍 Fetching PyPI versions...\n")
    pypi_versions = {}
    
    for md_file in md_files:
        content = md_file.read_text()
        base_name, packages = extract_package_info_from_md(content, md_file.name)
        
        # Fetch version for each package found
        for pkg_name in packages.keys():
            if pkg_name not in pypi_versions:
                print(f"Fetching {pkg_name}...", end=' ')
                version = get_latest_pypi_version(pkg_name)
                if version:
                    pypi_versions[pkg_name] = version
                    print(f"✅ {version}")
                else:
                    print("❌ Failed")
    
    print(f"\n{'='*60}")
    print("Processing release logs...\n")
    
    # Process each file
    modified_count = 0
    for md_file in md_files:
        print(f"Processing {md_file.name}...")
        if process_release_log(md_file, pypi_versions, dry_run=args.dry_run):
            modified_count += 1
        print()
    
    # Print summary
    print("="*60)
    print(f"Summary:")
    print(f"  Total files:     {len(md_files)}")
    if args.dry_run:
        print(f"  Would modify:    {modified_count}")
    else:
        print(f"  Modified:        {modified_count}")
    print(f"  Already updated: {len(md_files) - modified_count}")
    print("="*60)


if __name__ == "__main__":
    main()
