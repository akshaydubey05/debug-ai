"""
Log Parser - Parse and structure log entries
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import re
import json


@dataclass
class ParsedLog:
    """Structured log entry."""
    raw: str
    timestamp: Optional[datetime]
    level: str
    service: str
    message: str
    metadata: Dict[str, Any]
    error_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "raw": self.raw,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "service": self.service,
            "message": self.message,
            "metadata": self.metadata,
            "error_id": self.error_id,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute by key (dict-like access)."""
        return getattr(self, key, default)


class LogParser:
    """
    Parses raw log entries into structured format.
    Supports multiple log formats: JSON, Apache, Nginx, Syslog, and custom patterns.
    """
    
    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        (r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)", "%Y-%m-%dT%H:%M:%S"),
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d+)?)", "%Y-%m-%d %H:%M:%S"),
        (r"(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})", "%d/%b/%Y:%H:%M:%S"),
        (r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", None),  # Syslog
    ]
    
    # Log level patterns
    LEVEL_PATTERNS = [
        (r"\b(FATAL|CRITICAL)\b", "critical"),
        (r"\b(ERROR|ERR)\b", "error"),
        (r"\b(WARN|WARNING)\b", "warn"),
        (r"\b(INFO|NOTICE)\b", "info"),
        (r"\b(DEBUG|TRACE)\b", "debug"),
    ]
    
    def __init__(self):
        self._custom_patterns: List[tuple] = []
    
    def parse(self, entry: Dict[str, Any]) -> Optional["ParsedLog"]:
        """Parse a raw log entry."""
        raw = entry.get("raw", "")
        
        if not raw:
            return None
        
        # Try JSON first
        if raw.strip().startswith("{"):
            return self._parse_json(raw, entry)
        
        # Parse as text
        return self._parse_text(raw, entry)
    
    def _parse_json(self, raw: str, entry: Dict[str, Any]) -> Optional[ParsedLog]:
        """Parse JSON log entry."""
        try:
            data = json.loads(raw)
            
            # Extract common fields
            timestamp = self._extract_timestamp_from_json(data)
            level = self._extract_level_from_json(data)
            message = self._extract_message_from_json(data)
            service = data.get("service") or data.get("app") or entry.get("service", "unknown")
            
            # Everything else is metadata
            metadata = {k: v for k, v in data.items() 
                       if k not in ["timestamp", "time", "@timestamp", "level", "severity", 
                                   "message", "msg", "service", "app"]}
            
            return ParsedLog(
                raw=raw,
                timestamp=timestamp,
                level=level,
                service=service,
                message=message,
                metadata=metadata
            )
        except json.JSONDecodeError:
            return self._parse_text(raw, entry)
    
    def _parse_text(self, raw: str, entry: Dict[str, Any]) -> ParsedLog:
        """Parse text log entry."""
        timestamp = self._extract_timestamp(raw) or entry.get("timestamp")
        level = self._extract_level(raw) or entry.get("level", "info")
        service = entry.get("service", "unknown")
        message = self._extract_message(raw)
        
        # Try to extract additional metadata
        metadata = {}
        
        # Extract trace IDs
        trace_match = re.search(r"trace[_-]?id[=:]\s*([a-f0-9-]+)", raw, re.I)
        if trace_match:
            metadata["trace_id"] = trace_match.group(1)
        
        # Extract request IDs
        req_match = re.search(r"request[_-]?id[=:]\s*([a-f0-9-]+)", raw, re.I)
        if req_match:
            metadata["request_id"] = req_match.group(1)
        
        return ParsedLog(
            raw=raw,
            timestamp=timestamp,
            level=level,
            service=service,
            message=message,
            metadata=metadata
        )
    
    def _extract_timestamp(self, text: str) -> Optional[datetime]:
        """Extract timestamp from text."""
        for pattern, fmt in self.TIMESTAMP_PATTERNS:
            match = re.search(pattern, text)
            if match:
                ts_str = match.group(1)
                try:
                    if fmt:
                        # Handle various formats
                        ts_str = ts_str.replace(",", ".")
                        ts_str = re.sub(r"\.\d+", "", ts_str)  # Remove microseconds
                        ts_str = re.sub(r"Z$", "", ts_str)    # Remove Z
                        ts_str = re.sub(r"[+-]\d{2}:\d{2}$", "", ts_str)  # Remove timezone
                        return datetime.strptime(ts_str[:19], fmt[:len(ts_str)])
                except:
                    pass
        return None
    
    def _extract_timestamp_from_json(self, data: Dict) -> Optional[datetime]:
        """Extract timestamp from JSON data."""
        for key in ["timestamp", "time", "@timestamp", "ts", "datetime"]:
            if key in data:
                value = data[key]
                if isinstance(value, (int, float)):
                    return datetime.fromtimestamp(value)
                elif isinstance(value, str):
                    return self._extract_timestamp(value)
        return None
    
    def _extract_level(self, text: str) -> str:
        """Extract log level from text."""
        for pattern, level in self.LEVEL_PATTERNS:
            if re.search(pattern, text, re.I):
                return level
        return "info"
    
    def _extract_level_from_json(self, data: Dict) -> str:
        """Extract log level from JSON data."""
        for key in ["level", "severity", "loglevel", "log_level"]:
            if key in data:
                value = str(data[key]).lower()
                if value in ["fatal", "critical", "crit"]:
                    return "critical"
                elif value in ["error", "err"]:
                    return "error"
                elif value in ["warn", "warning"]:
                    return "warn"
                elif value in ["info", "notice"]:
                    return "info"
                elif value in ["debug", "trace"]:
                    return "debug"
        return "info"
    
    def _extract_message(self, text: str) -> str:
        """Extract the main message from log text."""
        # Remove timestamp
        for pattern, _ in self.TIMESTAMP_PATTERNS:
            text = re.sub(pattern, "", text)
        
        # Remove level
        for pattern, _ in self.LEVEL_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.I)
        
        # Clean up
        text = re.sub(r"^\s*[-:\[\]]+\s*", "", text)
        text = text.strip()
        
        return text or "No message"
    
    def _extract_message_from_json(self, data: Dict) -> str:
        """Extract message from JSON data."""
        for key in ["message", "msg", "text", "log", "error"]:
            if key in data:
                return str(data[key])
        return str(data)
    
    def add_custom_pattern(self, name: str, pattern: str, fields: List[str]) -> None:
        """Add a custom parsing pattern."""
        self._custom_patterns.append((name, re.compile(pattern), fields))
