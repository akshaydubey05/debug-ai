# DebugAI Documentation

Welcome to **DebugAI** - the AI-powered log analysis and debugging CLI that reduces debugging time by 60-75%.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Get up and running with DebugAI in minutes.

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-book-open-variant:{ .lg .middle } **User Guide**

    ---

    Learn how to use all of DebugAI's powerful features.

    [:octicons-arrow-right-24: Commands](guide/commands.md)

-   :material-code-braces:{ .lg .middle } **API Reference**

    ---

    Detailed API documentation for developers.

    [:octicons-arrow-right-24: API Docs](api/parser.md)

-   :material-github:{ .lg .middle } **Contributing**

    ---

    Help make DebugAI even better!

    [:octicons-arrow-right-24: Contribute](development/contributing.md)

</div>

## ✨ Features

### 🤖 AI-Powered Analysis
Uses Google Gemini to analyze errors and suggest intelligent fixes with confidence scores.

### 📖 Plain English Explanations
Transform cryptic stack traces into understandable explanations.

### 🔗 Cross-Service Correlation
Automatically trace errors across distributed systems and microservices.

### 📅 Timeline Generation
Visualize the sequence of events leading to crashes.

### 🐳 Docker Integration
Analyze container logs directly without manual exports.

### ⚡ Lightweight & Fast
No ELK stack required - works locally on your machine.

## 🎯 Why DebugAI?

| Traditional Debugging | With DebugAI |
|:---------------------|:-------------|
| ❌ Manually grep through thousands of log lines | ✅ AI identifies root causes instantly |
| ❌ Struggle to understand cryptic stack traces | ✅ Plain English explanations |
| ❌ Miss correlations between services | ✅ Automatic cross-service correlation |
| ❌ Hours to find the root cause | ✅ Minutes with AI-powered analysis |

## 🚀 Quick Example

```bash
# Analyze logs from a directory
debugai analyze path ./logs

# Get AI explanation for an error
debugai explain text "NullPointerException in UserService.getUser()"

# Analyze Docker container logs
debugai analyze docker my-api-container --tail 500

# Get fix suggestions
debugai suggest-fix text "Connection refused to database"
```

## 📦 Installation

```bash
pip install debugai
```

Or install from source:

```bash
git clone https://github.com/akshaydubey05/debug-ai.git
cd debug-ai/debugai
pip install -e ".[dev]"
```

## 🎮 Next Steps

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quickstart.md)
- [Command Reference](guide/commands.md)
- [API Documentation](api/parser.md)

## 🤝 Community

- **GitHub:** [akshaydubey05/debug-ai](https://github.com/akshaydubey05/debug-ai)
- **Issues:** [Report bugs or request features](https://github.com/akshaydubey05/debug-ai/issues)
- **Discussions:** [Join the conversation](https://github.com/akshaydubey05/debug-ai/discussions)

## 📄 License

DebugAI is released under the [MIT License](https://github.com/akshaydubey05/debug-ai/blob/main/LICENSE).
