"""
Gemini Client - Google Gemini AI integration

This module handles all AI-powered analysis using Google's Gemini API.
"""

from typing import Dict, Any, List, Optional
import os
import json


class GeminiClient:
    """
    Client for Google Gemini AI API.
    Handles error analysis, explanations, and fix suggestions.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            model: Model to use (default: gemini-2.0-flash)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model
        self._model = None
        self._initialized = False
    
    def _get_model(self):
        """Initialize and return the Gemini model."""
        if self._model is None:
            if not self.api_key:
                raise ValueError(
                    "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                    "or run 'debugai config set api-key YOUR_KEY'"
                )
            
            try:
                import google.generativeai as genai
                
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                self._initialized = True
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
        
        return self._model
    
    def analyze_errors(
        self,
        errors: List[Dict[str, Any]],
        context: str,
        max_errors: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze errors and provide insights.
        
        Args:
            errors: List of error entries
            context: Additional context from logs
            max_errors: Maximum errors to analyze
        
        Returns:
            Analysis results with root causes and suggestions
        """
        from debugai.ai.prompts import ERROR_ANALYSIS_PROMPT
        
        model = self._get_model()
        
        # Prepare error summary
        error_text = self._format_errors(errors[:max_errors])
        
        prompt = ERROR_ANALYSIS_PROMPT.format(
            errors=error_text,
            context=context[:4000],  # Limit context size
            error_count=len(errors)
        )
        
        try:
            response = model.generate_content(prompt)
            return self._parse_analysis_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "root_causes": [],
                "suggestions": [],
                "summary": f"Analysis failed: {e}"
            }
    
    def explain_error(
        self,
        error: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Explain an error in plain English.
        
        Args:
            error: Error entry to explain
            verbose: Include technical details
        
        Returns:
            Explanation dictionary
        """
        from debugai.ai.prompts import ERROR_EXPLANATION_PROMPT
        
        model = self._get_model()
        
        prompt = ERROR_EXPLANATION_PROMPT.format(
            error_message=error.get("message", error.get("raw", "")),
            error_level=error.get("level", "error"),
            service=error.get("service", "unknown"),
            timestamp=error.get("timestamp", "unknown"),
            verbose="Include detailed technical analysis." if verbose else ""
        )
        
        try:
            response = model.generate_content(prompt)
            return self._parse_explanation_response(response.text, verbose)
        except Exception as e:
            return {
                "summary": f"Could not explain error: {e}",
                "technical_details": None,
                "similar_issues": []
            }
    
    def explain_text(self, error_text: str) -> str:
        """
        Explain any error text directly.
        
        Args:
            error_text: Error message or stack trace
        
        Returns:
            Plain English explanation
        """
        from debugai.ai.prompts import TEXT_EXPLANATION_PROMPT
        
        model = self._get_model()
        
        prompt = TEXT_EXPLANATION_PROMPT.format(error_text=error_text)
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not explain: {e}"
    
    def suggest_fixes(
        self,
        error: Dict[str, Any],
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest fixes for an error.
        
        Args:
            error: Error entry
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of fix suggestions
        """
        from debugai.ai.prompts import FIX_SUGGESTION_PROMPT
        
        model = self._get_model()
        
        prompt = FIX_SUGGESTION_PROMPT.format(
            error_message=error.get("message", error.get("raw", "")),
            service=error.get("service", "unknown"),
            max_suggestions=max_suggestions
        )
        
        try:
            response = model.generate_content(prompt)
            return self._parse_suggestions_response(response.text, max_suggestions)
        except Exception as e:
            return [{
                "title": "Analysis Failed",
                "description": str(e),
                "confidence": 0,
                "code": None
            }]
    
    def suggest_for_text(
        self,
        error_text: str,
        language: str = "python",
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest fixes for any error text.
        
        Args:
            error_text: Error message
            language: Programming language
            max_suggestions: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        from debugai.ai.prompts import TEXT_FIX_PROMPT
        
        model = self._get_model()
        
        prompt = TEXT_FIX_PROMPT.format(
            error_text=error_text,
            language=language,
            max_suggestions=max_suggestions
        )
        
        try:
            response = model.generate_content(prompt)
            return self._parse_suggestions_response(response.text, max_suggestions)
        except Exception as e:
            return [{
                "title": "Analysis Failed",
                "description": str(e),
                "confidence": 0
            }]
    
    def correlate_errors(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Find correlations between errors.
        
        Args:
            errors: List of errors to correlate
        
        Returns:
            Correlation analysis
        """
        from debugai.ai.prompts import CORRELATION_PROMPT
        
        model = self._get_model()
        
        error_text = self._format_errors(errors[:20])
        prompt = CORRELATION_PROMPT.format(errors=error_text)
        
        try:
            response = model.generate_content(prompt)
            return self._parse_correlation_response(response.text)
        except Exception as e:
            return {"error": str(e), "correlations": []}
    
    def _format_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Format errors for prompt."""
        lines = []
        for i, error in enumerate(errors, 1):
            lines.append(f"{i}. [{error.get('level', 'ERROR')}] {error.get('service', 'unknown')}")
            lines.append(f"   Time: {error.get('timestamp', 'unknown')}")
            lines.append(f"   Message: {error.get('message', error.get('raw', ''))[:500]}")
            lines.append("")
        return "\n".join(lines)
    
    def _parse_analysis_response(self, text: str) -> Dict[str, Any]:
        """Parse AI analysis response."""
        result = {
            "root_causes": [],
            "suggestions": [],
            "summary": ""
        }
        
        # Try to parse as JSON first
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            elif text.strip().startswith("{"):
                return json.loads(text)
        except:
            pass
        
        # Parse text response
        lines = text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "root cause" in line.lower():
                current_section = "root_causes"
            elif "suggestion" in line.lower() or "fix" in line.lower():
                current_section = "suggestions"
            elif "summary" in line.lower():
                current_section = "summary"
            elif line and current_section:
                if current_section == "summary":
                    result["summary"] += line + " "
                elif current_section == "root_causes":
                    if line.startswith(("-", "*", "•", "1", "2", "3")):
                        result["root_causes"].append({
                            "title": line.lstrip("-*•0123456789. "),
                            "explanation": "",
                            "confidence": 70
                        })
                elif current_section == "suggestions":
                    if line.startswith(("-", "*", "•", "1", "2", "3")):
                        result["suggestions"].append({
                            "title": line.lstrip("-*•0123456789. "),
                            "description": "",
                            "code": None
                        })
        
        if not result["summary"]:
            result["summary"] = text[:500]
        
        return result
    
    def _parse_explanation_response(self, text: str, verbose: bool) -> Dict[str, Any]:
        """Parse explanation response."""
        result = {
            "summary": text,
            "technical_details": None,
            "similar_issues": []
        }
        
        if verbose and "\n\n" in text:
            parts = text.split("\n\n", 1)
            result["summary"] = parts[0]
            result["technical_details"] = parts[1] if len(parts) > 1 else None
        
        return result
    
    def _parse_suggestions_response(
        self,
        text: str,
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Parse suggestions response."""
        suggestions = []
        
        # Try JSON first
        try:
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data[:max_suggestions]
        except:
            pass
        
        # Parse text
        current_suggestion = None
        code_block = None
        in_code = False
        
        for line in text.split("\n"):
            if line.startswith("```") and not in_code:
                in_code = True
                code_block = []
                continue
            elif line.startswith("```") and in_code:
                in_code = False
                if current_suggestion and code_block:
                    current_suggestion["code"] = "\n".join(code_block)
                code_block = None
                continue
            
            if in_code and code_block is not None:
                code_block.append(line)
            elif line.strip().startswith(("1.", "2.", "3.", "-", "*", "•")):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {
                    "title": line.lstrip("-*•0123456789. ").strip(),
                    "description": "",
                    "confidence": 70,
                    "code": None
                }
            elif current_suggestion and line.strip():
                current_suggestion["description"] += line.strip() + " "
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions[:max_suggestions]
    
    def _parse_correlation_response(self, text: str) -> Dict[str, Any]:
        """Parse correlation response."""
        return {
            "correlations": [],
            "summary": text
        }
