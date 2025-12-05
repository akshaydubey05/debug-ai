<div align="center">

# 🔍 DebugAI

### AI-Powered Log Analysis & Debugging CLI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Built with Typer](https://img.shields.io/badge/Built%20with-Typer-009688?style=for-the-badge)](https://typer.tiangolo.com/)

<br/>

🚀 **Reduce debugging time by 60-75%** with AI-powered log analysis, error correlation, and intelligent fix suggestions.

<br/>

[✨ Features](#-features) •
[🚀 Quick Start](#-quick-start) •
[📖 Commands](#-commands) •
[⚙️ Configuration](#️-configuration) •
[🤝 Contributing](#-contributing)

---

</div>

## 🎯 Why DebugAI?

Tired of spending hours digging through logs? **DebugAI transforms cryptic error messages into actionable insights.**

| Traditional Debugging | With DebugAI |
|:---------------------|:-------------|
| ❌ Manually grep through thousands of log lines | ✅ AI identifies root causes instantly |
| ❌ Struggle to understand cryptic stack traces | ✅ Plain English explanations |
| ❌ Miss correlations between services | ✅ Automatic cross-service correlation |
| ❌ Hours to find the root cause | ✅ Minutes with AI-powered analysis |

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Analysis
Uses Google Gemini to analyze errors and suggest intelligent fixes with confidence scores.

### 📖 Plain English Explanations
No more cryptic stack traces - understand what went wrong in simple terms.

### 🔗 Cross-Service Correlation
Automatically traces errors across distributed systems and microservices.

### 📅 Timeline Generation
Visualize the sequence of events leading to crashes and failures.

</td>
<td width="50%">

### 🐳 Docker Integration
Analyze container logs directly from Docker without manual exports.

### 💡 Smart Fix Suggestions
Get actionable code fixes with confidence scores and explanations.

### ⚡ Lightweight & Fast
No ELK stack required - works locally on your machine.

### 🎨 Beautiful CLI
Rich, colorful output with multiple themes for better readability.

</td>
</tr>
</table>

---

## 🚀 Quick Start

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/debugai/debugai.git
cd debugai

# Install in development mode
pip install -e ".[dev]"

# Or install from PyPI (coming soon)
pip install debugai
```

### ⚙️ Setup

```bash
# Initialize DebugAI in your project
debugai init

# Set your Gemini API key
# Get one free at: https://makersuite.google.com/app/apikey
debugai config set api-key YOUR_GEMINI_API_KEY

# Or use environment variable
export GEMINI_API_KEY=your_api_key
```

### 🎮 Basic Usage

```bash
# Analyze log files
debugai analyze path ./logs

# Analyze specific services
debugai analyze path ./logs --service api,db,redis

# Analyze Docker container logs
debugai analyze docker my-container --tail 500

# Explain an error in plain English
debugai explain text "NullPointerException in UserService.getUser()"

# Get fix suggestions
debugai suggest-fix text "Connection refused to database"

# View event timeline
debugai timeline show --last 10m --filter errors
```

---

## 📖 Commands

<details>
<summary><strong>🔬 debugai analyze</strong> - Analyze logs from multiple sources</summary>

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
| Option | Description |
|--------|-------------|
| `--service, -s` | Filter by service names (comma-separated) |
| `--level, -l` | Filter by log level (error, warn, info, debug) |
| `--since` | Analyze logs since time (e.g., "1h", "30m") |
| `--correlate/--no-correlate` | Enable/disable cross-service correlation |
| `--ai/--no-ai` | Enable/disable AI analysis |
| `--format, -f` | Output format (rich, json, markdown) |
| `--save, -o` | Save report to file |

</details>

<details>
<summary><strong>💬 debugai explain</strong> - Get plain English explanations</summary>

```bash
# Explain by error ID
debugai explain error err_abc123

# Explain any error text
debugai explain text "FATAL: password authentication failed for user 'admin'"
```

**Options:**
| Option | Description |
|--------|-------------|
| `--verbose, -v` | Include detailed technical analysis |

</details>

<details>
<summary><strong>💡 debugai suggest-fix</strong> - Get AI-powered fix suggestions</summary>

```bash
# Get suggestions for an error ID
debugai suggest-fix error err_abc123

# Get suggestions for error text
debugai suggest-fix text "ModuleNotFoundError: No module named 'requests'"
```

**Options:**
| Option | Description |
|--------|-------------|
| `--max, -m` | Maximum number of suggestions (default: 3) |
| `--lang, -l` | Programming language hint |

</details>

<details>
<summary><strong>📅 debugai timeline</strong> - Generate event timelines</summary>

```bash
# Show recent events
debugai timeline show --last 5m

# Filter by level
debugai timeline show --last 1h --filter errors

# Trace events leading to a crash
debugai timeline crash err_abc123 --before 10m
```

**Options:**
| Option | Description |
|--------|-------------|
| `--last, -l` | Time range (e.g., "5m", "1h", "1d") |
| `--filter, -f` | Filter: errors, warnings, all |
| `--service, -s` | Filter by service |
| `--limit, -n` | Maximum events to show |

</details>

<details>
<summary><strong>📁 debugai logs</strong> - Manage log sources</summary>

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

</details>

<details>
<summary><strong>⚙️ debugai config</strong> - Manage configuration</summary>

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

</details>

<details>
<summary><strong>🖥️ debugai interactive</strong> - Start interactive session</summary>

```bash
debugai interactive start
```

</details>

---

## 🎬 Demo

<details>
<summary><strong>Click to see DebugAI in action</strong></summary>

### Analyzing Logs

```bash
$ debugai analyze path ./sample_logs --service api,db,redis
```

### Example Output

```
╭─────────────────────────────────────────────────────────────╮
│                  🔬 DebugAI Log Analysis                    │
╰─────────────────────────────────────────────────────────────╯

📊 Total Log Entries    10,432
❌ Errors Found         23
⚠️  Warnings Found       156
🎯 Root Causes          2
💡 Suggestions          5

╭─────────────────────────────────────────────────────────────╮
│                   🤖 AI Analysis                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎯 Root Cause #1: Database Connection Pool Exhausted      │
│                                                             │
│  The application is running out of database connections    │
│  because connections are not being properly released.      │
│  This started at 14:23:45 and cascaded to the API layer.   │
│                                                             │
│  Confidence: 92%                                           │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

💡 Suggested Fixes:

  1. Increase Connection Pool Size
     Add connection pool configuration to prevent exhaustion.

     engine = create_engine(
         DATABASE_URL,
         pool_size=20,
         max_overflow=10,
         pool_pre_ping=True
     )

  2. Add Connection Timeout
     Ensure connections are released after timeout.
```

</details>

---

## 🐳 Docker Integration

DebugAI seamlessly integrates with Docker to analyze container logs:

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

## ⚙️ Configuration

DebugAI can be configured through multiple methods:

### 1️⃣ Environment Variables

```bash
export GEMINI_API_KEY=your_api_key
export DEBUGAI_MODEL=gemini-1.5-pro
export DEBUGAI_FORMAT=json
```

### 2️⃣ Config File

Create `.debugai/config.yaml` in your project:

```yaml
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

### 3️⃣ Command Line Options

Override any setting via CLI flags.

---

## 🛠️ Development

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

### 📁 Project Structure

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
├── sample_logs/          # Sample log files
└── pyproject.toml        # Project config
```

---

## 🗺️ Roadmap

| Status | Feature | Description |
|:------:|---------|-------------|
| 🔲 | **Kubernetes Integration** | Analyze logs from K8s pods |
| 🔲 | **Prometheus/Grafana** | Correlate metrics with logs |
| 🔲 | **Custom AI Providers** | OpenAI, Anthropic, local LLMs |
| 🔲 | **VS Code Extension** | Analyze logs in your editor |
| 🔲 | **Web Dashboard** | Browser-based interface |
| 🔲 | **Pattern Learning** | Learn from codebase patterns |
| 🔲 | **Team Collaboration** | Share insights and reports |

---

## ❓ FAQ

<details>
<summary><strong>How do I get a Gemini API key?</strong></summary>

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to create a free API key. The free tier includes generous usage limits for personal and development use.
</details>

<details>
<summary><strong>What log formats are supported?</strong></summary>

DebugAI automatically detects and parses:
- ✅ Standard text logs (INFO, WARN, ERROR, DEBUG)
- ✅ JSON structured logs
- ✅ Apache/Nginx access logs
- ✅ Docker container logs
- ✅ Syslog format
- ✅ Custom formats via configuration
</details>

<details>
<summary><strong>Is my data sent to external servers?</strong></summary>

Only when using AI features - log snippets are sent to Google Gemini for analysis. You can disable AI with `--no-ai` flag for offline analysis. All storage is local by default.
</details>

<details>
<summary><strong>Can I use this in production?</strong></summary>

Yes! DebugAI is designed for production use. Use the `--no-ai` flag if you have sensitive data, or configure data redaction in `config.yaml`.
</details>

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

| Type | Description |
|------|-------------|
| 🐛 **Report Bugs** | Open an issue describing the problem |
| 💡 **Suggest Features** | Share your ideas in discussions |
| 🔧 **Submit PRs** | Fork, make changes, and submit a pull request |

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## 🙏 Acknowledgments

- 🤖 Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- ⌨️ Built with [Typer](https://typer.tiangolo.com/) CLI framework
- 🎨 Beautiful output with [Rich](https://rich.readthedocs.io/)

---

<div align="center">

### ⭐ Star History

If you find DebugAI useful, please consider giving it a star!  
It helps others discover the project.

<br/>

[![GitHub stars](https://img.shields.io/github/stars/debugai/debugai?style=social)](https://github.com/debugai/debugai)

<br/>

**[⬆ Back to Top](#-debugai)**

---

Made with ❤️ by developers, for developers who hate debugging

</div>
