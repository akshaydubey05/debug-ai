# PyPI Publishing Guide for DebugAI

This guide explains how to publish DebugAI to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email

2. **Test PyPI Account** (Optional but recommended)
   - Create account at https://test.pypi.org/account/register/

3. **API Tokens**
   - Generate API token at https://pypi.org/manage/account/token/
   - Add to GitHub Secrets as `PYPI_API_TOKEN`

## Manual Publishing (One-time setup)

### 1. Install Build Tools

```bash
pip install build twine hatchling
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build
```

This creates:
- `dist/debugai-1.0.0-py3-none-any.whl` (wheel)
- `dist/debugai-1.0.0.tar.gz` (source distribution)

### 3. Check the Build

```bash
twine check dist/*
```

### 4. Test on Test PyPI (Optional)

```bash
twine upload --repository testpypi dist/*
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ debugai
```

### 5. Upload to PyPI

```bash
twine upload dist/*
```

Enter your PyPI username and password (or token).

### 6. Verify

Visit https://pypi.org/project/debugai/

Test installation:
```bash
pip install debugai
```

## Automated Publishing (Recommended)

Publishing is automated via GitHub Actions when you create a release tag.

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "1.0.1"  # Increment version
```

### 2. Update Changelog

Edit `CHANGELOG.md`:
```markdown
## [1.0.1] - 2026-02-15

### Added
- New feature X

### Fixed
- Bug Y
```

### 3. Commit and Tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Release v1.0.1"
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin main --tags
```

### 4. Automatic Release

GitHub Actions will automatically:
1. ✅ Create GitHub Release
2. ✅ Build package
3. ✅ Publish to PyPI
4. ✅ Deploy documentation

## Setup GitHub Secrets

Add these secrets to your repository:

1. Go to: `Settings` → `Secrets and variables` → `Actions`
2. Add secret: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backwards compatible
- **PATCH** (x.x.1): Bug fixes, backwards compatible

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature
- `1.9.0` → `2.0.0`: Breaking change

## Pre-release Versions

For alpha/beta releases:

```toml
version = "1.1.0a1"  # Alpha
version = "1.1.0b1"  # Beta
version = "1.1.0rc1" # Release Candidate
```

## Troubleshooting

### Package Already Exists

PyPI doesn't allow re-uploading the same version. Increment the version number.

### Build Fails

Check:
- ✅ All files in MANIFEST.in exist
- ✅ No syntax errors in pyproject.toml
- ✅ All dependencies are specified

### Import Errors After Install

Ensure package structure:
```
src/
  debugai/
    __init__.py
    ...
```

### Missing Files in Package

Check MANIFEST.in and rebuild:
```bash
python -m build --no-isolation
```

## Best Practices

1. ✅ Always test on Test PyPI first
2. ✅ Use automated releases via GitHub Actions
3. ✅ Update CHANGELOG.md before release
4. ✅ Tag releases with `git tag`
5. ✅ Never commit API tokens to git
6. ✅ Increment version for every release
7. ✅ Write release notes in GitHub Releases

## Resources

- [PyPI Documentation](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
