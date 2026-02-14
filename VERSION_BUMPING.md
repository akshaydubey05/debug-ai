# Version Bumping Guide

DebugAI supports automatic version bumping with three options: **major**, **minor**, and **patch** (bugfix).

## Version Format

We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─── Bug fixes, backwards compatible (0.0.1 → 0.0.2)
  │     └───────── New features, backwards compatible (0.0.0 → 0.1.0)
  └─────────────── Breaking changes (0.0.0 → 1.0.0)
```

### Examples:

| Current | Bump Type | New Version | Use Case |
|---------|-----------|-------------|----------|
| 1.0.0 | **major** | 2.0.0 | Breaking changes, major new features |
| 1.0.0 | **minor** | 1.1.0 | New features, backwards compatible |
| 1.0.0 | **patch** | 1.0.1 | Bug fixes, small improvements |

---

## 🚀 Method 1: GitHub Actions (Recommended)

### Automated Version Bump via GitHub UI

1. **Go to your repository on GitHub**
2. **Click on "Actions" tab**
3. **Select "Bump Version and Release" workflow**
4. **Click "Run workflow" dropdown**
5. **Select version type:**
   - `major` - Breaking changes (1.0.0 → 2.0.0)
   - `minor` - New features (1.0.0 → 1.1.0)
   - `patch` - Bug fixes (1.0.0 → 1.0.1)
6. **Click "Run workflow"**

### What Happens Automatically:

1. ✅ Bumps version in `pyproject.toml`
2. ✅ Updates `CHANGELOG.md` with new version
3. ✅ Commits changes
4. ✅ Creates git tag (e.g., `v1.0.1`)
5. ✅ Creates GitHub Release
6. ✅ Publishes to PyPI
7. ✅ Deploys documentation

**That's it! Everything is automated!** 🎉

---

## 🛠️ Method 2: Local Python Script

### Using the bump_version.py script

```bash
# Navigate to debugai directory
cd debugai

# Bump major version (1.0.0 → 2.0.0)
python bump_version.py major

# Bump minor version (1.0.0 → 1.1.0)
python bump_version.py minor

# Bump patch version (1.0.0 → 1.0.1)
python bump_version.py patch
```

The script will:
1. Show current and new version
2. Ask for confirmation
3. Update `pyproject.toml`
4. Update `CHANGELOG.md`
5. Show next steps

**Then manually:**
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

---

## 📝 Method 3: Manual Version Bump

### Step-by-Step Manual Process

1. **Edit `pyproject.toml`**
   ```toml
   [project]
   version = "1.0.1"  # Change this
   ```

2. **Edit `CHANGELOG.md`**
   ```markdown
   ## [1.0.1] - 2026-02-14
   
   ### Fixed
   - Bug fix description
   
   ### Added
   - New feature description
   ```

3. **Commit changes**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 1.0.1"
   git push origin main
   ```

4. **Create tag**
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

The tag triggers automatic release workflow! 🚀

---

## 📊 When to Use Each Version Type

### 🔴 Major Version (X.0.0)

**Use when:**
- Breaking API changes
- Removing features
- Major architectural changes
- Incompatible with previous versions

**Examples:**
```
1.5.3 → 2.0.0
- Removed deprecated `analyze_text()` function
- Changed CLI argument structure
- Requires Python 3.12+ instead of 3.11+
```

### 🟡 Minor Version (0.X.0)

**Use when:**
- Adding new features
- New functionality (backwards compatible)
- Deprecating features (but not removing)
- Significant improvements

**Examples:**
```
1.0.5 → 1.1.0
- Added support for Elasticsearch logs
- New command: debugai export
- Added 3 new themes
```

### 🟢 Patch Version (0.0.X)

**Use when:**
- Bug fixes
- Performance improvements
- Documentation updates
- Security patches
- Small tweaks

**Examples:**
```
1.1.0 → 1.1.1
- Fixed NullPointerException in parser
- Improved error messages
- Updated dependencies
- Fixed typos in docs
```

---

## 🔄 Complete Release Workflow

### Quick Release (GitHub Actions)

```bash
# 1. Make your changes and commit
git add .
git commit -m "Add new feature X"
git push origin main

# 2. Go to GitHub → Actions → "Bump Version and Release"
# 3. Select version type and click "Run workflow"
# 4. Done! ✅
```

### Full Manual Release

```bash
# 1. Make changes
git add .
git commit -m "Add feature X"

# 2. Bump version
python bump_version.py minor

# 3. Review changes
git diff

# 4. Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.1.0"

# 5. Tag and push
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main --tags

# 6. GitHub Actions does the rest!
```

---

## 🎯 Best Practices

1. ✅ **Always update CHANGELOG.md** with what changed
2. ✅ **Test before releasing** - run tests locally
3. ✅ **Use semantic versioning** correctly
4. ✅ **Write clear commit messages**
5. ✅ **Tag releases** with annotated tags (`-a`)
6. ✅ **Review GitHub Release** after automation completes

---

## 🐛 Troubleshooting

### Version bump failed

**Check:**
- Are you on the main branch?
- Do you have latest changes pulled?
- Is the version in pyproject.toml valid?

### Tag already exists

```bash
# Delete local tag
git tag -d v1.0.1

# Delete remote tag
git push origin :refs/tags/v1.0.1

# Create new tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

### PyPI upload failed

**Check:**
- Is PYPI_API_TOKEN set in GitHub Secrets?
- Has this version already been published?
- You cannot re-upload the same version to PyPI

---

## 📚 Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 🚀 Quick Reference

```bash
# GitHub Actions (Automated) - RECOMMENDED
Actions → Bump Version and Release → Select type → Run

# Local Script
python bump_version.py major|minor|patch

# Manual
# 1. Edit pyproject.toml and CHANGELOG.md
# 2. git commit -m "Bump version to X.Y.Z"
# 3. git tag -a vX.Y.Z -m "Release vX.Y.Z"
# 4. git push origin main --tags
```

**Remember:** Once you push a tag starting with `v`, everything else is automatic! 🎉
