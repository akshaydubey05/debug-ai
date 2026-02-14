# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WebSocket support for real-time log streaming
- Support for Elasticsearch integration
- Custom plugin system
- Web dashboard

## [1.0.0] - 2026-02-14

### Added
- 🎉 Initial release of DebugAI
- AI-powered log analysis using Google Gemini
- Cross-service error correlation engine
- Timeline generation for event sequences
- Docker container log integration
- Real-time log streaming and analysis
- 8 beautiful CLI themes (Cyan, Green, Red, Purple, Orange, Blue, Matrix, Hacker)
- Interactive debugging mode
- Comprehensive stress testing suite
- Support for multiple log formats (JSON, Apache, Nginx, Syslog)

### Features
- **Log Analysis**
  - Parse logs from files, directories, and Docker containers
  - Detect error patterns automatically
  - Categorize errors by type and severity
  - Generate detailed statistics

- **AI Capabilities**
  - Plain English error explanations
  - Smart fix suggestions with confidence scores
  - Context-aware analysis
  - Error correlation across services

- **CLI Interface**
  - Rich, colorful terminal output
  - Multiple export formats (Rich, JSON, Markdown)
  - Progress indicators and animations
  - Customizable themes

- **Developer Tools**
  - Comprehensive API documentation
  - Type hints throughout codebase
  - Unit and stress tests
  - Docker support

### Documentation
- Complete user guide
- API reference documentation
- Quick start tutorial
- Configuration examples

### Dependencies
- Python 3.11+ support
- Google Generative AI SDK
- Typer for CLI framework
- Rich for terminal formatting
- SQLAlchemy for storage
- Docker SDK for container integration

---

## Release Process

To create a new release:

1. Update version in `pyproject.toml`
2. Update this CHANGELOG.md
3. Commit changes: `git commit -m "Release vX.Y.Z"`
4. Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push: `git push origin main --tags`
6. GitHub Actions will automatically:
   - Create GitHub release
   - Build and publish to PyPI
   - Deploy documentation

## Version History

- **v1.0.0** (2026-02-14) - Initial public release
