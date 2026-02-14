# 🚀 Complete Setup Guide for Professional Publishing

This guide walks you through setting up DebugAI for professional publishing to PyPI with automated releases and documentation.

## 📋 What's Been Set Up

### 1. GitHub Actions CI/CD ✅
- **`.github/workflows/ci.yml`** - Continuous Integration
  - Runs tests on every push/PR
  - Tests on multiple OS (Ubuntu, Windows, macOS)
  - Tests on Python 3.11 and 3.12
  - Code quality checks (Ruff, Black, MyPy)
  - Stress tests
  - Code coverage reporting

- **`.github/workflows/release.yml`** - Automated Releases
  - Triggers on version tags (e.g., `v1.0.0`)
  - Creates GitHub Release
  - Publishes to PyPI
  - Deploys documentation to GitHub Pages

### 2. Documentation Website ✅
- **MkDocs with Material theme** configured
- **Complete documentation structure:**
  - Getting Started guides
  - User guides
  - API reference
  - Development docs
  - FAQ and Changelog

### 3. PyPI Publishing ✅
- **`pyproject.toml`** - Properly configured
- **`MANIFEST.in`** - Package includes
- **`CHANGELOG.md`** - Version history
- **Publishing guide** included

## 🔧 Setup Steps

### Step 1: Configure GitHub Secrets

1. **Get PyPI API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create new token with name "debugai-github-actions"
   - Scope: "Entire account" or "Project: debugai"
   - Copy the token (starts with `pypi-`)

2. **Add to GitHub**
   - Go to your repo: https://github.com/akshaydubey05/debug-ai
   - Click `Settings` → `Secrets and variables` → `Actions`
   - Click `New repository secret`
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token
   - Click `Add secret`

### Step 2: Enable GitHub Pages

1. Go to `Settings` → `Pages`
2. Source: `Deploy from a branch`
3. Branch: `gh-pages` (will be created automatically)
4. Folder: `/ (root)`
5. Click `Save`

### Step 3: Test Locally

#### Test Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve locally
mkdocs serve
```

Visit http://127.0.0.1:8000

#### Test Build

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check build
twine check dist/*
```

### Step 4: Create Your First Release

#### Option A: Test on Test PyPI First (Recommended)

1. **Get Test PyPI Token**
   - Go to https://test.pypi.org/manage/account/token/
   - Create token
   - Add to GitHub Secrets as `TEST_PYPI_API_TOKEN`

2. **Upload to Test PyPI**
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Test Installation**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ debugai
   ```

#### Option B: Go Live Immediately

1. **Update version if needed** (already set to 1.0.0)
   
2. **Commit all changes**
   ```bash
   git add .
   git commit -m "Add professional publishing setup"
   git push origin add-stress-tests
   ```

3. **Merge to main**
   - Create and merge your pull request
   - Or push directly to main

4. **Create release tag**
   ```bash
   git checkout main
   git pull
   git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
   git push origin v1.0.0
   ```

5. **Watch the magic happen! ✨**
   - Go to `Actions` tab in GitHub
   - Watch the `Release & Publish` workflow run
   - It will:
     - ✅ Create GitHub Release
     - ✅ Publish to PyPI
     - ✅ Deploy documentation

### Step 5: Verify Everything Works

1. **Check GitHub Release**
   - https://github.com/akshaydubey05/debug-ai/releases

2. **Check PyPI**
   - https://pypi.org/project/debugai/

3. **Check Documentation**
   - https://akshaydubey05.github.io/debug-ai/

4. **Test Installation**
   ```bash
   pip install debugai
   debugai --version
   ```

## 📊 Continuous Workflow

For future releases:

### 1. Make Changes
```bash
git checkout -b feature/new-feature
# Make your changes
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. Create Pull Request
- CI will automatically run tests
- Review and merge when green ✅

### 3. Release New Version

```bash
# Update version in pyproject.toml
version = "1.1.0"

# Update CHANGELOG.md
## [1.1.0] - 2026-XX-XX
### Added
- New feature X

# Commit
git add pyproject.toml CHANGELOG.md
git commit -m "Release v1.1.0"
git push origin main

# Tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

GitHub Actions handles the rest! 🎉

## 🎯 What Users Will See

### On PyPI
```bash
pip install debugai
```

### In README
```markdown
[![PyPI version](https://badge.fury.io/py/debugai.svg)](https://badge.fury.io/py/debugai)
[![Downloads](https://pepy.tech/badge/debugai)](https://pepy.tech/project/debugai)
[![CI Status](https://github.com/akshaydubey05/debug-ai/workflows/CI/badge.svg)](https://github.com/akshaydubey05/debug-ai/actions)
```

### Documentation Site
Beautiful, searchable documentation at:
https://akshaydubey05.github.io/debug-ai/

## 🐛 Troubleshooting

### Release Workflow Fails

**Problem:** PyPI upload fails
- **Check:** API token is correct in GitHub Secrets
- **Check:** Version number hasn't been used before
- **Fix:** Increment version number

**Problem:** Documentation deploy fails
- **Check:** GitHub Pages is enabled
- **Check:** Branch `gh-pages` exists
- **Fix:** First run creates it automatically

### Package Not Found on PyPI

**Wait 5-10 minutes** after release for PyPI to index.

### Documentation Not Updating

**Check:**
- GitHub Pages enabled?
- Workflow completed successfully?
- Clear browser cache

## 📝 Best Practices

1. ✅ **Always update CHANGELOG.md** before release
2. ✅ **Test on Test PyPI first** for major releases
3. ✅ **Use semantic versioning** (MAJOR.MINOR.PATCH)
4. ✅ **Write good commit messages**
5. ✅ **Keep documentation up to date**
6. ✅ **Run tests locally** before pushing
7. ✅ **Review CI results** before merging

## 🎓 Learn More

- [Semantic Versioning](https://semver.org/)
- [Python Packaging](https://packaging.python.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

## 🚀 You're Ready!

Your project is now set up for professional publishing! 

**Next steps:**
1. Add PyPI token to GitHub Secrets
2. Create your first release tag
3. Watch it deploy automatically
4. Share with the world! 🌍
