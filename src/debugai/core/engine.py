"""
Debug Engine - Core orchestration for log analysis

This is the main engine that coordinates all analysis operations.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class LogEntry:
    """Represents a single log entry."""
    raw: str
    timestamp: Optional[datetime] = None
    level: str = "info"
    service: str = "unknown"
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw": self.raw,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "service": self.service,
            "message": self.message,
            "metadata": self.metadata,
            "error_id": self.error_id,
        }


@dataclass
class AnalysisResult:
    """Result of log analysis."""
    total_entries: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    root_causes: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    timeline: List[Dict[str, Any]] = field(default_factory=list)


class DebugEngine:
    """
    Main debugging engine that orchestrates all analysis operations.
    """
    
    def __init__(self):
        self._parsed_logs: List[LogEntry] = []
        self._errors: List[Dict[str, Any]] = []
        self._error_index: Dict[str, Dict[str, Any]] = {}
    
    def parse_logs(self, raw_logs: List[Dict[str, Any]]) -> List[Any]:
        """Parse raw log entries into structured log objects."""
        from debugai.ingestion.parser import LogParser, ParsedLog
        
        parser = LogParser()
        self._parsed_logs = []
        
        for raw in raw_logs:
            entry = parser.parse(raw)
            if entry:
                # Generate error ID for errors
                if entry.level in ("error", "critical", "fatal"):
                    entry.error_id = self._generate_error_id(entry)
                    self._error_index[entry.error_id] = entry.to_dict()
                
                self._parsed_logs.append(entry)
        
        return self._parsed_logs
    
    def identify_errors(self, logs: List[Any]) -> List[Dict[str, Any]]:
        """Identify and extract errors from parsed logs."""
        errors = []
        
        for entry in logs:
            level = entry.level if hasattr(entry, 'level') else entry.get('level', 'info')
            if level in ("error", "critical", "fatal", "exception"):
                if hasattr(entry, 'to_dict'):
                    error_dict = entry.to_dict()
                else:
                    error_dict = dict(entry)
                
                error_id = getattr(entry, 'error_id', None) or self._generate_error_id(entry)
                error_dict["error_id"] = error_id
                errors.append(error_dict)
                
                # Store in index
                self._error_index[error_dict["error_id"]] = error_dict
        
        self._errors = errors
        return errors
    
    def ai_analyze(
        self,
        errors: List[Dict[str, Any]],
        context: List[LogEntry],
        max_errors: int = 50
    ) -> Dict[str, Any]:
        """Run AI-powered analysis on errors."""
        from debugai.ai.gemini_client import GeminiClient
        
        ai = GeminiClient()
        
        # Prepare context
        context_text = self._prepare_context(context, errors)
        
        # Get AI analysis
        analysis = ai.analyze_errors(
            errors=errors[:max_errors],
            context=context_text
        )
        
        return analysis
    
    def get_error_by_id(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an error by its ID."""
        # Check in-memory index first
        if error_id in self._error_index:
            return self._error_index[error_id]
        
        # Check database
        from debugai.storage.database import Database
        db = Database()
        return db.get_error(error_id)
    
    def quick_analyze(self, path: str) -> Dict[str, Any]:
        """Quick analysis of a log file or directory."""
        from debugai.ingestion.file_ingester import FileIngester
        
        ingester = FileIngester()
        logs = ingester.ingest(Path(path))
        
        parsed = self.parse_logs(logs)
        errors = self.identify_errors(parsed)
        
        return {
            "total_entries": len(parsed),
            "error_count": len(errors),
            "errors": errors[:10],  # First 10 errors
        }
    
    def _generate_error_id(self, entry: Any) -> str:
        """Generate a unique ID for an error."""
        if hasattr(entry, 'service'):
            service = entry.service
            message = entry.message
            level = entry.level
        else:
            service = entry.get('service', 'unknown')
            message = entry.get('message', '')
            level = entry.get('level', 'error')
        
        content = f"{service}:{message}:{level}"
        return "err_" + hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _prepare_context(
        self,
        logs: List[Any],
        errors: List[Dict[str, Any]]
    ) -> str:
        """Prepare context string for AI analysis."""
        lines = []
        
        # Add recent log entries around errors
        for error in errors[:10]:
            lines.append(f"ERROR: {error.get('message', 'Unknown')}")
            lines.append(f"  Service: {error.get('service', 'Unknown')}")
            lines.append(f"  Time: {error.get('timestamp', 'Unknown')}")
            lines.append("")
        
        return "\n".join(lines)
