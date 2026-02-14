# Quick Start

Get started with DebugAI in just a few minutes!

## 1. Initialize DebugAI

After installation, initialize DebugAI in your project:

```bash
debugai init
```

This creates a `.debugai` directory with default configuration.

## 2. Configure API Key

Set your Gemini API key:

```bash
debugai config set api-key YOUR_GEMINI_API_KEY
```

Or use an environment variable:

```bash
export GEMINI_API_KEY=your_api_key
```

## 3. Analyze Your First Logs

### From Files

```bash
# Analyze all logs in a directory
debugai analyze path ./logs

# Analyze with filters
debugai analyze path ./logs --service api --level error
```

### From Docker

```bash
# Analyze a container's logs
debugai analyze docker my-container

# Analyze multiple containers
debugai analyze docker api db redis --tail 1000
```

### Real-time Streaming

```bash
# Stream and analyze a log file
debugai analyze stream /var/log/app.log

# From stdin
tail -f app.log | debugai analyze stream stdin
```

## 4. Understand Errors

Get plain English explanations:

```bash
debugai explain text "NullPointerException in UserService.getUser()"
```

## 5. Get Fix Suggestions

```bash
debugai suggest-fix text "ModuleNotFoundError: No module named 'requests'"
```

## 6. View Timeline

See what happened before a crash:

```bash
debugai timeline show --last 1h --filter errors
```

## Example Workflow

Here's a complete debugging workflow:

```bash
# 1. Analyze logs from your application
debugai analyze path ./logs --service api,db

# 2. Get detailed explanation of a specific error
debugai explain error err_abc123

# 3. Get AI-powered fix suggestions
debugai suggest-fix error err_abc123

# 4. View the timeline of events
debugai timeline show --error err_abc123

# 5. Export the analysis
debugai analyze path ./logs --format json --save report.json
```

## Interactive Mode

For an interactive experience:

```bash
debugai interactive
```

This starts an interactive session where you can:
- ✅ Analyze logs step by step
- ✅ Ask questions about errors
- ✅ Get real-time suggestions
- ✅ Explore correlations

## Themes

DebugAI comes with 8 beautiful themes:

```bash
# List available themes
debugai config list-themes

# Set a theme
debugai config set theme matrix

# Try different themes
debugai config set theme hacker
debugai config set theme purple
```

## Next Steps

- [Learn about all commands](../guide/commands.md)
- [Explore AI features](../guide/ai-features.md)
- [Configure DebugAI](configuration.md)
- [Docker integration](../guide/docker.md)
