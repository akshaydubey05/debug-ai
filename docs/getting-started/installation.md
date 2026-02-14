# Installation

## Requirements

- Python 3.11 or higher
- pip package manager
- Google Gemini API key (free tier available)

## Install from PyPI

The easiest way to install DebugAI is via pip:

```bash
pip install debugai
```

To verify the installation:

```bash
debugai --version
```

## Install from Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/akshaydubey05/debug-ai.git
cd debug-ai/debugai

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Install with Optional Dependencies

### Documentation Tools

```bash
pip install debugai[docs]
```

### Development Tools

```bash
pip install debugai[dev]
```

This includes:
- pytest (testing)
- ruff (linting)
- black (formatting)
- mypy (type checking)
- pre-commit (git hooks)

## Docker Installation

Run DebugAI in a Docker container:

```bash
docker pull debugai/debugai:latest

docker run -it --rm \
  -v $(pwd)/logs:/logs \
  -e GEMINI_API_KEY=your_api_key \
  debugai/debugai analyze path /logs
```

## Get Gemini API Key

DebugAI uses Google's Gemini AI for intelligent analysis. Get your free API key:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

!!! tip "Free Tier"
    The Gemini API offers a generous free tier with 60 requests per minute - perfect for most debugging workflows!

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration](configuration.md)
- [Commands Overview](../guide/commands.md)
