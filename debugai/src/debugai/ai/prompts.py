"""
AI Prompts - Prompt templates for Gemini AI

These prompts are carefully engineered for optimal debugging assistance.
"""

# Error Analysis Prompt
ERROR_ANALYSIS_PROMPT = """You are an expert debugging assistant analyzing application logs.

## Errors Found ({error_count} total):
{errors}

## Additional Context:
{context}

## Your Task:
Analyze these errors and provide:

1. **Root Cause Analysis**: Identify the primary root cause(s) of these errors
2. **Error Correlation**: Explain how these errors might be related
3. **Impact Assessment**: What is the likely impact on the system?
4. **Suggested Fixes**: Provide actionable fix suggestions with code examples
5. **Prevention**: How can these errors be prevented in the future?

Respond in this JSON format:
```json
{{
  "root_causes": [
    {{
      "title": "Brief title",
      "explanation": "Detailed explanation",
      "confidence": 85,
      "affected_services": ["service1", "service2"]
    }}
  ],
  "suggestions": [
    {{
      "title": "Fix title",
      "description": "What to do",
      "code": "example code if applicable",
      "language": "python",
      "priority": "high"
    }}
  ],
  "summary": "Plain English summary of what happened and why"
}}
```
"""

# Error Explanation Prompt
ERROR_EXPLANATION_PROMPT = """You are a helpful debugging assistant. Explain this error in plain English that any developer can understand.

## Error Details:
- **Level**: {error_level}
- **Service**: {service}
- **Time**: {timestamp}
- **Message**: {error_message}

{verbose}

## Instructions:
1. Explain what this error means in simple terms
2. Explain why this error typically occurs
3. Describe the potential impact
4. If there's a stack trace, explain the flow

Keep your explanation clear and actionable. Avoid jargon unless necessary, and explain any technical terms you use.
"""

# Text Explanation Prompt
TEXT_EXPLANATION_PROMPT = """You are a helpful debugging assistant. Explain this error or log message in plain English:

```
{error_text}
```

Provide:
1. **What it means**: A clear, simple explanation
2. **Why it happens**: Common causes
3. **What to do**: Quick steps to investigate or fix

Keep it concise and practical.
"""

# Fix Suggestion Prompt
FIX_SUGGESTION_PROMPT = """You are an expert developer helping to fix an error.

## Error:
- **Service**: {service}
- **Message**: {error_message}

## Your Task:
Provide {max_suggestions} actionable fix suggestions.

For each suggestion, provide:
1. A clear title
2. Step-by-step description
3. Code example if applicable
4. Confidence level (0-100)

Respond in JSON format:
```json
[
  {{
    "title": "Fix Title",
    "description": "Detailed steps to fix",
    "code": "// code example",
    "language": "python",
    "confidence": 85
  }}
]
```
"""

# Text Fix Prompt
TEXT_FIX_PROMPT = """You are an expert {language} developer helping to fix an error.

## Error:
```
{error_text}
```

Provide {max_suggestions} specific, actionable fixes.

For each fix:
1. Clear title
2. What to change and why
3. Code example
4. Confidence percentage

Respond in JSON format:
```json
[
  {{
    "title": "Fix Title",
    "description": "What to do",
    "code": "corrected code",
    "language": "{language}",
    "confidence": 80
  }}
]
```
"""

# Error Correlation Prompt
CORRELATION_PROMPT = """You are analyzing multiple errors to find correlations and the root cause.

## Errors:
{errors}

## Analyze:
1. Are these errors related? How?
2. What's the sequence of events that led to these errors?
3. Which error is the root cause, and which are symptoms?
4. What service or component is the common factor?

Provide a clear analysis of how these errors are connected and what the underlying issue is.
"""

# Timeline Analysis Prompt
TIMELINE_PROMPT = """Analyze this sequence of events and explain what happened:

## Event Timeline:
{events}

## Questions to Answer:
1. What triggered the initial problem?
2. How did the error propagate through the system?
3. What was the cascade effect?
4. At what point could intervention have prevented the failure?

Provide a narrative explanation of the incident timeline.
"""

# Pattern Detection Prompt
PATTERN_PROMPT = """Analyze these log patterns and identify:

## Patterns Found:
{patterns}

## Identify:
1. Which patterns indicate problems?
2. Are there any anomalies?
3. What do these patterns suggest about system health?
4. Any recommendations for alerting or monitoring?

Provide actionable insights based on these patterns.
"""
