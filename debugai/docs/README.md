# Building Documentation

DebugAI uses [MkDocs](https://www.mkdocs.org/) with the [Material](https://squidfunk.github.io/mkdocs-material/) theme for documentation.

## Local Development

### Install Dependencies

```bash
pip install -e ".[docs]"
```

### Serve Locally

```bash
mkdocs serve
```

Visit http://127.0.0.1:8000 in your browser.

The site will automatically reload when you make changes to the documentation files.

### Build Documentation

```bash
mkdocs build
```

This creates a `site/` directory with the static website.

## Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/
│   ├── installation.md         # Installation guide
│   ├── quickstart.md          # Quick start tutorial
│   └── configuration.md       # Configuration reference
├── guide/
│   ├── commands.md            # Commands reference
│   ├── analysis.md            # Log analysis guide
│   ├── correlation.md         # Error correlation
│   ├── ai-features.md         # AI capabilities
│   ├── docker.md              # Docker integration
│   └── themes.md              # Themes guide
├── api/
│   ├── parser.md              # Parser API
│   ├── analyzer.md            # Analyzer API
│   ├── ai-client.md          # AI Client API
│   └── database.md            # Database API
├── development/
│   ├── contributing.md        # Contributing guide
│   ├── architecture.md        # Architecture overview
│   ├── testing.md             # Testing guide
│   └── release.md             # Release process
├── faq.md                     # FAQ
└── changelog.md               # Changelog
```

## Writing Documentation

### Markdown Files

Use standard Markdown with extensions:

````markdown
# Page Title

## Section

Regular text with **bold** and *italic*.

### Code Blocks

```python
import debugai

# Code example
analyzer = debugai.LogAnalyzer()
```

### Admonitions

!!! note "Optional Title"
    This is a note

!!! tip
    Helpful tip

!!! warning
    Warning message

!!! danger
    Danger alert

### Tables

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

### Links

[Link text](page.md)
[External](https://example.com)
````

### API Documentation

Use mkdocstrings for auto-generated API docs:

````markdown
::: debugai.parser.LogParser
    options:
      show_source: true
      members:
        - parse
        - parse_file
````

## Deployment

### Automatic (Recommended)

Documentation is automatically deployed to GitHub Pages when you create a release tag.

### Manual

```bash
# Build
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Preview Before Merging

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve locally
mkdocs serve

# Check for broken links
mkdocs build --strict
```

## Style Guide

### Tone
- Clear and concise
- Friendly and helpful
- Assume beginner level unless in advanced sections

### Code Examples
- Always test code examples
- Include imports
- Show expected output when relevant
- Use real-world examples

### Screenshots
- Use PNG format
- Optimize images (<200KB)
- Place in `docs/images/`
- Use descriptive filenames

### Headers
- Use sentence case
- Don't skip header levels
- Keep headers descriptive

### Links
- Use relative links for internal pages
- Full URLs for external links
- Add `target="_blank"` for external links

## Troubleshooting

### Port Already in Use

```bash
mkdocs serve -a 127.0.0.1:8001
```

### Theme Not Loading

```bash
pip install --upgrade mkdocs-material
```

### Broken Links

```bash
mkdocs build --strict
```

This will fail if there are broken links.
