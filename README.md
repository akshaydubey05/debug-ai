# 🔍 DebugAI - AI-Powered Log Analysis & Debugging CLI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Reduce debugging time by 60-75%** with AI-powered log analysis, error correlation, and intelligent fix suggestions.

---

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses Google Gemini to analyze errors and suggest fixes
- 📖 **Plain English Explanations** - No more cryptic stack traces
- 🔗 **Cross-Service Correlation** - Traces errors across distributed systems
- 📅 **Timeline Generation** - See events leading to crashes
- 🐳 **Docker Integration** - Analyze container logs directly
- 💡 **Smart Fix Suggestions** - Get actionable code fixes
- ⚡ **Lightweight** - No ELK stack required, works locally

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd debugai

# Install in development mode
pip install -e ".[dev]"

# Or install from PyPI (when published)
pip install debugai
```

### Setup

```bash
# Initialize DebugAI in your project
debugai init

# Set your Gemini API key
debugai config set api-key YOUR_GEMINI_API_KEY

# Or use environment variable
export GEMINI_API_KEY=your_api_key
```

### Basic Usage

```bash
# Analyze log files
debugai analyze path ./logs

# Analyze specific services
debugai analyze path ./logs --service api,db,redis

# Analyze Docker container logs
debugai analyze docker my-container --tail 500

# Explain an error
debugai explain text "NullPointerException in UserService.getUser()"

# Get fix suggestions
debugai suggest-fix text "Connection refused to database"

# View event timeline
debugai timeline show --last 10m --filter errors
```

---

## 📖 Commands

### `debugai analyze`

Analyze logs from multiple sources.

```bash
# Analyze files
debugai analyze path ./logs
debugai analyze path ./logs --service api,db --level error

# Analyze Docker containers
debugai analyze docker container_name
debugai analyze docker api db redis --tail 1000

# Stream analysis (real-time)
debugai analyze stream /var/log/app.log
tail -f app.log | debugai analyze stream stdin
```

**Options:**
- `--service, -s` - Filter by service names (comma-separated)
- `--level, -l` - Filter by log level (error, warn, info, debug)
- `--since` - Analyze logs since time (e.g., "1h", "30m")
- `--correlate/--no-correlate` - Enable/disable cross-service correlation
- `--ai/--no-ai` - Enable/disable AI analysis
- `--format, -f` - Output format (rich, json, markdown)
- `--save, -o` - Save report to file

### `debugai explain`

Get plain English explanations for errors.

```bash
# Explain by error ID
debugai explain error err_abc123

# Explain any error text
debugai explain text "FATAL: password authentication failed for user 'admin'"
```

**Options:**
- `--verbose, -v` - Include detailed technical analysis

### `debugai suggest-fix`

Get AI-powered fix suggestions.

```bash
# Get suggestions for an error ID
debugai suggest-fix error err_abc123

# Get suggestions for error text
debugai suggest-fix text "ModuleNotFoundError: No module named 'requests'"
```

**Options:**
- `--max, -m` - Maximum number of suggestions (default: 3)
- `--lang, -l` - Programming language hint

### `debugai timeline`

Generate event timelines.

```bash
# Show recent events
debugai timeline show --last 5m

# Filter by level
debugai timeline show --last 1h --filter errors

# Trace events leading to a crash
debugai timeline crash err_abc123 --before 10m
```

**Options:**
- `--last, -l` - Time range (e.g., "5m", "1h", "1d")
- `--filter, -f` - Filter: errors, warnings, all
- `--service, -s` - Filter by service
- `--limit, -n` - Maximum events to show

### `debugai logs`

Manage log sources.

```bash
# Add a log source
debugai logs add ./logs --name app-logs --service api

# List configured sources
debugai logs list

# Remove a source
debugai logs remove app-logs

# Watch logs in real-time
debugai logs watch
```

### `debugai config`

Manage configuration.

```bash
# Set configuration
debugai config set api-key YOUR_KEY
debugai config set model gemini-1.5-pro

# Get configuration
debugai config get model

# List all settings
debugai config list

# Reset to defaults
debugai config reset --yes
```

### `debugai interactive`

Start an interactive debugging session.

```bash
debugai interactive start
```

---

## ⚙️ Configuration

DebugAI can be configured through:

1. **Environment variables**
2. **Config file** (`.debugai/config.yaml`)
3. **Command line options**

### Environment Variables

```bash
export GEMINI_API_KEY=your_api_key
export DEBUGAI_MODEL=gemini-1.5-pro
export DEBUGAI_FORMAT=json
```

### Config File

```yaml
# .debugai/config.yaml

ai:
  provider: gemini
  model: gemini-1.5-flash
  max_tokens: 4096
  temperature: 0.3

analysis:
  correlation: true
  max_errors: 100
  correlation_window: 60

output:
  format: rich
  theme: auto
  timestamps: true

storage:
  database: .debugai/debugai.db
  cache_ttl: 24
```

---

## 🐳 Docker Integration

DebugAI can analyze logs directly from Docker containers:

```bash
# Single container
debugai analyze docker my-api

# Multiple containers
debugai analyze docker api db redis cache

# Follow logs in real-time
debugai analyze docker my-api --follow

# Specify time range
debugai analyze docker my-api --since 1h --tail 1000
```

---

## 📊 Example Output

```
╭─────────────────────────────────────────────────────────────╮
│                  🔬 DebugAI Log Analysis                     │
╰─────────────────────────────────────────────────────────────╯

📊 Total Log Entries    10,432
❌ Errors Found         23
⚠️ Warnings Found       156
🎯 Root Causes          2
💡 Suggestions          5

╭─────────────────────────────────────────────────────────────╮
│                   🤖 AI Analysis                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎯 Root Cause #1: Database Connection Pool Exhausted       │
│                                                              │
│  The application is running out of database connections     │
│  because connections are not being properly released.       │
│  This started at 14:23:45 and cascaded to the API layer.   │
│                                                              │
│  Confidence: 92%                                            │
│                                                              │
╰─────────────────────────────────────────────────────────────╯

💡 Suggested Fixes:

  1. Increase Connection Pool Size
     Add connection pool configuration to prevent exhaustion.

     ```python
     engine = create_engine(
         DATABASE_URL,
         pool_size=20,
         max_overflow=10,
         pool_pre_ping=True
     )
     ```

  2. Add Connection Timeout
     Ensure connections are released after timeout.
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/debugai/debugai.git
cd debugai

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
black src/
mypy src/
```

### Project Structure

```
debugai/
├── src/debugai/
│   ├── cli/              # CLI commands
│   │   ├── main.py       # Entry point
│   │   └── commands/     # Command modules
│   ├── core/             # Core engine
│   │   ├── engine.py     # Main orchestrator
│   │   └── analyzer.py   # Pattern analysis
│   ├── ingestion/        # Log ingestion
│   │   ├── file_ingester.py
│   │   ├── docker_ingester.py
│   │   └── parser.py
│   ├── ai/               # AI integration
│   │   ├── gemini_client.py
│   │   └── prompts.py
│   ├── analysis/         # Analysis modules
│   │   ├── correlator.py
│   │   └── timeline_builder.py
│   ├── storage/          # Data storage
│   │   └── database.py
│   └── config/           # Configuration
│       └── settings.py
├── tests/                # Test suite
├── docs/                 # Documentation
└── pyproject.toml        # Project config
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

---

## 🙏 Acknowledgments

- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)

---

<p align="center">
  <b>Made with ❤️ for developers who hate debugging</b>
</p>
