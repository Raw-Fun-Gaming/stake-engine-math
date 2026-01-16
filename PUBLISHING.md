# Publishing Guide

This guide explains how to publish the Stake Engine Math SDK to PyPI (Python Package Index), the equivalent of npm for Python projects.

---

## 📦 Publishing to PyPI

PyPI is the official Python package repository, similar to npm for TypeScript/JavaScript projects.

**Your package will be available at:**
- **PyPI:** https://pypi.org/project/stake-engine-math/
- **Install command:** `pip install stake-engine-math`

---

## 🚀 Quick Start

### 1. Install Build Tools

```bash
pip install --upgrade build twine
```

### 2. Create Distribution

```bash
# Build source distribution and wheel
python -m build

# Output:
# dist/
#   ├── stake-engine-math-2.0.0.tar.gz
#   └── stake_engine_math-2.0.0-py3-none-any.whl
```

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ stake-engine-math
```

### 4. Publish to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*

# You'll be prompted for:
# - Username: Your PyPI username or __token__
# - Password: Your PyPI password or API token
```

### 5. Verify

```bash
# Install from PyPI
pip install stake-engine-math

# Verify version
python -c "import stake_engine_math; print('Installed successfully!')"
```

---

## 🔑 API Token Setup (Recommended)

Using API tokens is more secure than passwords:

### Create PyPI API Token

1. **Create account:** https://pypi.org/account/register/
2. **Add API token:** https://pypi.org/manage/account/#api-tokens
3. **Scope:** Project-specific or Account-wide

### Configure Token

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...  # Your token here

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw...  # TestPyPI token
```

**Security:** Make sure `~/.pypirc` has restrictive permissions:
```bash
chmod 600 ~/.pypirc
```

---

## 📋 Pre-Publishing Checklist

Before publishing, ensure:

- [ ] **Version updated** in `setup.py` (currently `2.0.0`)
- [ ] **CHANGELOG.md** updated with release notes
- [ ] **README.md** badges and links correct
- [ ] **All tests passing:** `make test` (54 tests)
- [ ] **Code quality checks pass:** `make lint` or `pre-commit run --all-files`
- [ ] **Git tag created:** `git tag v2.0.0` and pushed
- [ ] **GitHub release published:** https://github.com/Raw-Fun-Gaming/stake-engine-math/releases
- [ ] **License file** present (MIT recommended)
- [ ] **Author email** updated in `setup.py`

---

## 🔄 Complete Publishing Workflow

### Version Update Workflow

```bash
# 1. Update version in setup.py
# Change: version="2.0.0" → version="2.1.0"

# 2. Update CHANGELOG.md
# Add new section for v2.1.0

# 3. Commit changes
git add setup.py CHANGELOG.md
git commit -m "chore: Bump version to 2.1.0"

# 4. Create and push tag
git tag v2.1.0
git push origin main --tags

# 5. Build distribution
python -m build

# 6. Upload to PyPI
python -m twine upload dist/*

# 7. Create GitHub release
gh release create v2.1.0 --title "v2.1.0" --notes "See CHANGELOG.md"

# 8. Verify installation
pip install --upgrade stake-engine-math
```

---

## 🎯 PyPI vs GitHub Comparison

| Feature | PyPI | GitHub |
|---------|------|--------|
| **Purpose** | Package distribution | Source code hosting |
| **Install** | `pip install stake-engine-math` | `git clone` |
| **Equivalent** | npm registry | GitHub repo |
| **Versioning** | Semantic versioning | Git tags |
| **Discovery** | `pip search` / pypi.org | GitHub search |
| **Stats** | Download counts | Stars, forks, watchers |
| **Documentation** | README on PyPI | docs/ + GitHub Pages |

**Best Practice:** Use both!
- **PyPI:** For easy installation via pip
- **GitHub:** For source code, issues, PRs, documentation

---

## 📊 Package Metrics & Badges

Once published to PyPI, add these badges to README.md:

```markdown
[![PyPI version](https://img.shields.io/pypi/v/stake-engine-math?style=flat-square)](https://pypi.org/project/stake-engine-math/)
[![PyPI downloads](https://img.shields.io/pypi/dm/stake-engine-math?style=flat-square)](https://pypi.org/project/stake-engine-math/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stake-engine-math?style=flat-square)](https://pypi.org/project/stake-engine-math/)
```

**Tracking:**
- Downloads: https://pypistats.org/packages/stake-engine-math
- Ranking: https://hugovk.github.io/top-pypi-packages/

---

## 🔍 Alternative/Additional Platforms

### 1. **Conda-Forge** (Recommended for Scientific Packages)
- **URL:** https://conda-forge.org/
- **Install:** `conda install -c conda-forge stake-engine-math`
- **Good for:** Data science, scientific computing users

### 2. **GitHub Packages**
- **URL:** https://github.com/features/packages
- **Install:** `pip install git+https://github.com/Raw-Fun-Gaming/stake-engine-math.git`
- **Good for:** Private packages, enterprise use

### 3. **Read the Docs** (Documentation)
- **URL:** https://readthedocs.org/
- **Purpose:** Auto-build and host documentation
- **Good for:** Comprehensive docs with search

---

## 🛠️ Build Automation

### GitHub Actions CI/CD

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**Setup:**
1. Add `PYPI_API_TOKEN` to GitHub Secrets
2. When you create a GitHub release, package auto-publishes to PyPI

---

## 📝 Example: Publishing v2.0.0

```bash
# Ensure everything is committed
git status

# Build
python -m build
# Output: dist/stake-engine-math-2.0.0*

# Check package
twine check dist/*
# Output: Checking dist/stake-engine-math-2.0.0.tar.gz: PASSED
#         Checking dist/stake_engine_math-2.0.0-py3-none-any.whl: PASSED

# Upload to PyPI
twine upload dist/*
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading stake-engine-math-2.0.0.tar.gz
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB
# Uploading stake_engine_math-2.0.0-py3-none-any.whl
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.0/60.0 kB

# View on PyPI
open https://pypi.org/project/stake-engine-math/

# Test installation
pip install stake-engine-math
# Successfully installed stake-engine-math-2.0.0
```

---

## ⚠️ Important Notes

### Version Constraints
- **Cannot overwrite** existing versions on PyPI
- Must increment version for each release
- Use semantic versioning: `MAJOR.MINOR.PATCH`

### File Exclusions
The following are automatically excluded from the package:
- `tests/`
- `games/` (example games)
- `scripts/` (development scripts)
- `utils/` (internal utilities)

Only the `src/` directory is included in the distribution.

### Private vs Public
- **Public PyPI:** Anyone can install
- **Private options:**
  - GitHub Packages (for organization)
  - Private PyPI server (e.g., devpi, Artifactory)
  - Direct git installs with access control

---

## 🎓 Learning Resources

- **PyPI Guide:** https://packaging.python.org/tutorials/packaging-projects/
- **Setuptools Docs:** https://setuptools.pypa.io/en/latest/
- **Twine Docs:** https://twine.readthedocs.io/en/latest/
- **PEP 517/518:** Modern Python packaging standards

---

## 🆘 Troubleshooting

### "Package already exists"
- **Cause:** Version already published
- **Fix:** Increment version in `setup.py`

### "Invalid distribution"
- **Cause:** Missing metadata
- **Fix:** Run `twine check dist/*` for details

### "Authentication failed"
- **Cause:** Wrong credentials
- **Fix:** Check `~/.pypirc` or re-enter API token

### "Module not found" after install
- **Cause:** Package structure issue
- **Fix:** Ensure `src/` has `__init__.py` files

---

**Ready to publish?** Follow the Quick Start section above! 🚀
