# Configuration

DebugAI can be configured through multiple methods:

1. Configuration file (`.debugai/config.yaml`)
2. Environment variables
3. Command-line arguments
4. Interactive CLI

## Configuration File

When you run `debugai init`, a configuration file is created at `.debugai/config.yaml`:

```yaml
# DebugAI Configuration

# AI Settings
ai:
  provider: gemini
  api_key: ${GEMINI_API_KEY}  # Use environment variable
  model: gemini-1.5-pro
  temperature: 0.3
  max_tokens: 2048

# Analysis Settings
analysis:
  enable_correlation: true
  correlation_window: 300  # seconds
  min_confidence: 0.7
  max_suggestions: 3

# UI Settings
ui:
  theme: cyan
  show_progress: true
  animations: true
  
# Storage Settings
storage:
  database_path: .debugai/debugai.db
  cache_enabled: true
  cache_ttl: 3600  # seconds

# Log Parsing
parser:
  timezone: UTC
  date_formats:
    - "%Y-%m-%d %H:%M:%S"
    - "%Y-%m-%dT%H:%M:%S"
    - "%d/%b/%Y:%H:%M:%S"
```

## Environment Variables

Override configuration with environment variables:

```bash
# AI Configuration
export GEMINI_API_KEY=your_api_key
export DEBUGAI_AI_MODEL=gemini-1.5-flash
export DEBUGAI_AI_TEMPERATURE=0.5

# Analysis
export DEBUGAI_ENABLE_CORRELATION=true
export DEBUGAI_MIN_CONFIDENCE=0.8

# UI
export DEBUGAI_THEME=matrix
export DEBUGAI_ANIMATIONS=false

# Storage
export DEBUGAI_DB_PATH=/custom/path/debugai.db
```

## CLI Configuration Commands

### View Current Configuration

```bash
debugai config show
```

### Set Values

```bash
# Set API key
debugai config set api-key YOUR_KEY

# Set theme
debugai config set theme hacker

# Set AI model
debugai config set ai-model gemini-1.5-flash

# Enable/disable correlation
debugai config set correlation true
```

### List Options

```bash
# List all themes
debugai config list-themes

# List all AI models
debugai config list-models
```

### Reset to Defaults

```bash
debugai config reset
```

## Advanced Configuration

### Custom Log Formats

Add custom log format patterns:

```yaml
parser:
  custom_patterns:
    - name: "my_app"
      pattern: '(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<message>.*)'
      timestamp_format: "%Y-%m-%d %H:%M:%S"
```

### Correlation Rules

Define custom correlation rules:

```yaml
analysis:
  correlation_rules:
    - name: "db_connection_timeout"
      pattern: "connection.*timeout"
      related_services: ["database", "api"]
      window: 60  # seconds
```

### AI Prompts

Customize AI prompts:

```yaml
ai:
  prompts:
    explain: "Explain this error in simple terms: {error}"
    suggest_fix: "Suggest fixes for: {error}"
    correlate: "Find correlations between these errors: {errors}"
```

## Per-Project Configuration

You can have different configurations for different projects:

```bash
# Initialize in project directory
cd /path/to/project
debugai init

# This creates .debugai/config.yaml in the current directory
```

DebugAI will use the nearest `.debugai/config.yaml` file in the directory tree.

## Configuration Priority

Configuration is loaded in this order (highest priority first):

1. Command-line arguments
2. Environment variables
3. Project configuration (`.debugai/config.yaml`)
4. User configuration (`~/.debugai/config.yaml`)
5. Default values

## Example Configurations

### Minimal Setup

```yaml
ai:
  api_key: ${GEMINI_API_KEY}
```

### Performance-Optimized

```yaml
ai:
  model: gemini-1.5-flash  # Faster model
  max_tokens: 1024

analysis:
  enable_correlation: false  # Skip correlation for speed

storage:
  cache_enabled: true
  cache_ttl: 7200
```

### Maximum Accuracy

```yaml
ai:
  model: gemini-1.5-pro
  temperature: 0.1  # More deterministic
  max_tokens: 4096

analysis:
  enable_correlation: true
  correlation_window: 600
  min_confidence: 0.9
  max_suggestions: 5
```

## Next Steps

- [Learn about commands](../guide/commands.md)
- [Explore AI features](../guide/ai-features.md)
- [API Reference](../api/parser.md)
