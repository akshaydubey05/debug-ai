# Commands Reference

Complete reference for all DebugAI commands.

## debugai analyze

Analyze logs from various sources.

### analyze path

Analyze logs from files or directories.

```bash
debugai analyze path <path> [OPTIONS]
```

**Arguments:**
- `path`: Path to log file or directory

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--service` | `-s` | Filter by service names (comma-separated) | all |
| `--level` | `-l` | Filter by log level | all |
| `--since` | | Analyze logs since time (e.g., "1h", "30m") | all time |
| `--until` | | Analyze logs until time | now |
| `--correlate/--no-correlate` | | Enable/disable correlation | true |
| `--ai/--no-ai` | | Enable/disable AI analysis | true |
| `--format` | `-f` | Output format (rich, json, markdown) | rich |
| `--save` | `-o` | Save report to file | - |

**Examples:**

```bash
# Analyze all logs in directory
debugai analyze path ./logs

# Filter by service and level
debugai analyze path ./logs --service api,db --level error

# Analyze last hour only
debugai analyze path ./logs --since 1h

# Save as JSON
debugai analyze path ./logs --format json --save report.json
```

### analyze docker

Analyze Docker container logs.

```bash
debugai analyze docker <containers...> [OPTIONS]
```

**Arguments:**
- `containers`: One or more container names/IDs

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--tail` | | Number of recent log lines | 1000 |
| `--follow` | `-f` | Stream logs in real-time | false |
| All options from `analyze path` | | | |

**Examples:**

```bash
# Analyze single container
debugai analyze docker my-api

# Analyze multiple containers
debugai analyze docker api db redis

# Real-time streaming
debugai analyze docker api --follow

# Last 500 lines
debugai analyze docker api --tail 500
```

### analyze stream

Analyze log streams in real-time.

```bash
debugai analyze stream <source> [OPTIONS]
```

**Arguments:**
- `source`: File path or `stdin`

**Options:**
- All options from `analyze path`

**Examples:**

```bash
# Stream from file
debugai analyze stream /var/log/app.log

# From stdin
tail -f app.log | debugai analyze stream stdin

# With filters
debugai analyze stream app.log --level error --ai
```

## debugai explain

Get plain English explanations for errors.

```bash
debugai explain {error|text} <input> [OPTIONS]
```

**Subcommands:**

### explain error

Explain by error ID from previous analysis.

```bash
debugai explain error <error_id>
```

### explain text

Explain any error text.

```bash
debugai explain text "<error_message>"
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Include technical details | false |
| `--context` | `-c` | Include surrounding context | true |

**Examples:**

```bash
# Explain by ID
debugai explain error err_abc123

# Explain text
debugai explain text "NullPointerException at line 42"

# Verbose explanation
debugai explain text "Connection timeout" --verbose
```

## debugai suggest-fix

Get AI-powered fix suggestions.

```bash
debugai suggest-fix {error|text} <input> [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--max` | `-m` | Maximum suggestions | 3 |
| `--lang` | `-l` | Programming language hint | auto |
| `--confidence` | | Minimum confidence threshold | 0.7 |

**Examples:**

```bash
# Get suggestions
debugai suggest-fix text "ModuleNotFoundError: No module named 'requests'"

# Limit suggestions
debugai suggest-fix error err_123 --max 5

# Specify language
debugai suggest-fix text "undefined variable" --lang python
```

## debugai timeline

View event timelines.

```bash
debugai timeline show [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--last` | | Time window (e.g., "1h", "30m") | 1h |
| `--error` | `-e` | Focus on specific error | - |
| `--service` | `-s` | Filter by services | all |
| `--filter` | `-f` | Filter type (all, errors, warnings) | all |

**Examples:**

```bash
# Show last hour
debugai timeline show --last 1h

# Focus on error
debugai timeline show --error err_123

# Filter errors only
debugai timeline show --filter errors
```

## debugai config

Manage configuration.

### config show

Display current configuration.

```bash
debugai config show
```

### config set

Set configuration value.

```bash
debugai config set <key> <value>
```

**Examples:**

```bash
debugai config set api-key YOUR_KEY
debugai config set theme matrix
debugai config set ai-model gemini-1.5-flash
```

### config list-themes

List available themes.

```bash
debugai config list-themes
```

### config reset

Reset to default configuration.

```bash
debugai config reset
```

## debugai init

Initialize DebugAI in current directory.

```bash
debugai init [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing configuration |

## debugai interactive

Start interactive debugging session.

```bash
debugai interactive [OPTIONS]
```

Interactive commands:
- `/analyze <path>` - Analyze logs
- `/explain <error>` - Explain error
- `/suggest <error>` - Get suggestions
- `/timeline` - Show timeline
- `/help` - Show help
- `/quit` - Exit

## debugai doctor

Check DebugAI health and configuration.

```bash
debugai doctor
```

Checks:
- ✅ Python version
- ✅ Dependencies installed
- ✅ API key configured
- ✅ Database accessible
- ✅ Network connectivity

## debugai logs

Manage DebugAI's internal logs.

```bash
debugai logs [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--tail` | Show last N lines |
| `--follow` | Stream logs |
| `--clear` | Clear log history |

## Global Options

Available for all commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-V` | Show version |
| `--verbose` | `-v` | Verbose output |
| `--quiet` | `-q` | Minimal output |
| `--no-color` | | Disable colors |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | API error |
| 4 | File not found |
| 5 | Permission denied |
