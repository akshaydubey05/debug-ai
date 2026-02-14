#!/usr/bin/env python3
"""
Version Bump Script for DebugAI

Usage:
    python bump_version.py major    # 1.0.0 -> 2.0.0
    python bump_version.py minor    # 1.0.0 -> 1.1.0
    python bump_version.py patch    # 1.0.0 -> 1.0.1
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def get_current_version(pyproject_path: Path) -> str:
    """Extract current version from pyproject.toml"""
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type"""
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def update_pyproject(pyproject_path: Path, old_version: str, new_version: str):
    """Update version in pyproject.toml"""
    content = pyproject_path.read_text()
    content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"')
    pyproject_path.write_text(content)
    print(f"✓ Updated {pyproject_path}")


def update_changelog(changelog_path: Path, new_version: str, bump_type: str):
    """Add entry to CHANGELOG.md"""
    content = changelog_path.read_text()
    today = datetime.now().strftime('%Y-%m-%d')
    
    new_entry = f"""
## [{new_version}] - {today}

### Changed
- Version bump: {bump_type} release

"""
    
    # Insert after [Unreleased] section
    content = content.replace('## [Unreleased]', f'## [Unreleased]\n{new_entry}')
    changelog_path.write_text(content)
    print(f"✓ Updated {changelog_path}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print(__doc__)
        sys.exit(1)
    
    bump_type = sys.argv[1]
    
    # Paths
    base_dir = Path(__file__).parent
    pyproject_path = base_dir / 'pyproject.toml'
    changelog_path = base_dir / 'CHANGELOG.md'
    
    # Get current version
    current_version = get_current_version(pyproject_path)
    print(f"Current version: {current_version}")
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")
    
    # Confirm
    response = input(f"\nBump version from {current_version} to {new_version}? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    # Update files
    update_pyproject(pyproject_path, current_version, new_version)
    update_changelog(changelog_path, new_version, bump_type)
    
    print(f"\n✅ Version bumped to {new_version}")
    print("\nNext steps:")
    print(f"  git add pyproject.toml CHANGELOG.md")
    print(f"  git commit -m 'Bump version to {new_version}'")
    print(f"  git tag -a v{new_version} -m 'Release v{new_version}'")
    print(f"  git push origin main --tags")


if __name__ == '__main__':
    main()
