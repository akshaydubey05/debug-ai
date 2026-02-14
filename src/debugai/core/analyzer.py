"""
Log Analyzer - Pattern detection and analysis
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from collections import defaultdict


@dataclass
class Pattern:
    """Represents a detected log pattern."""
    template: str
    count: int
    level: str
    examples: List[str]
    services: List[str]


class LogAnalyzer:
    """
    Analyzes logs to detect patterns, anomalies, and correlations.
    """
    
    # Common error patterns
    ERROR_PATTERNS = [
        (r"(?i)exception|error|failed|failure", "error"),
        (r"(?i)warning|warn", "warning"),
        (r"(?i)timeout|timed out", "timeout"),
        (r"(?i)connection refused|connection reset", "connection"),
        (r"(?i)out of memory|oom|memory", "memory"),
        (r"(?i)permission denied|access denied|unauthorized", "permission"),
        (r"(?i)not found|404|missing", "not_found"),
        (r"(?i)null pointer|nullptr|nil|undefined", "null_reference"),
    ]
    
    def __init__(self):
        self._patterns: Dict[str, Pattern] = {}
        self._error_clusters: List[Dict[str, Any]] = []
    
    def analyze(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive analysis on logs."""
        return {
            "patterns": self.detect_patterns(logs),
            "error_types": self.categorize_errors(logs),
            "anomalies": self.detect_anomalies(logs),
            "hot_spots": self.find_hot_spots(logs),
            "statistics": self.calculate_statistics(logs),
        }
    
    def detect_patterns(self, logs: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect recurring patterns in logs."""
        pattern_counts = defaultdict(lambda: {"count": 0, "examples": [], "services": set()})
        
        for log in logs:
            message = log.get("message", "")
            # Normalize message (replace numbers, IDs, etc.)
            template = self._normalize_message(message)
            
            pattern_counts[template]["count"] += 1
            if len(pattern_counts[template]["examples"]) < 3:
                pattern_counts[template]["examples"].append(message)
            pattern_counts[template]["services"].add(log.get("service", "unknown"))
        
        # Convert to Pattern objects
        patterns = []
        for template, data in pattern_counts.items():
            if data["count"] > 1:  # Only patterns that occur more than once
                patterns.append(Pattern(
                    template=template,
                    count=data["count"],
                    level=self._detect_level(template),
                    examples=data["examples"],
                    services=list(data["services"])
                ))
        
        # Sort by count
        patterns.sort(key=lambda p: p.count, reverse=True)
        return patterns[:50]  # Top 50 patterns
    
    def categorize_errors(self, logs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize errors by type."""
        categories = defaultdict(list)
        
        for log in logs:
            if log.get("level") in ("error", "critical", "fatal"):
                message = log.get("message", "")
                category = self._categorize_error(message)
                categories[category].append(log)
        
        return dict(categories)
    
    def detect_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in log patterns."""
        anomalies = []
        
        # Detect sudden spikes in error rate
        error_counts = defaultdict(int)
        for log in logs:
            if log.get("timestamp"):
                minute = log["timestamp"][:16]  # Group by minute
                if log.get("level") in ("error", "critical"):
                    error_counts[minute] += 1
        
        if error_counts:
            avg = sum(error_counts.values()) / len(error_counts)
            for minute, count in error_counts.items():
                if count > avg * 3:  # 3x average is anomaly
                    anomalies.append({
                        "type": "error_spike",
                        "time": minute,
                        "count": count,
                        "average": avg,
                        "severity": "high"
                    })
        
        return anomalies
    
    def find_hot_spots(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find services or components with most errors."""
        service_errors = defaultdict(int)
        
        for log in logs:
            if log.get("level") in ("error", "critical"):
                service = log.get("service", "unknown")
                service_errors[service] += 1
        
        hot_spots = [
            {"service": service, "error_count": count}
            for service, count in sorted(service_errors.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return hot_spots[:10]
    
    def calculate_statistics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate log statistics."""
        level_counts = defaultdict(int)
        service_counts = defaultdict(int)
        
        for log in logs:
            level_counts[log.get("level", "unknown")] += 1
            service_counts[log.get("service", "unknown")] += 1
        
        return {
            "total": len(logs),
            "by_level": dict(level_counts),
            "by_service": dict(service_counts),
            "error_rate": level_counts.get("error", 0) / max(len(logs), 1) * 100,
        }
    
    def _normalize_message(self, message: str) -> str:
        """Normalize a message to create a template."""
        # Replace numbers
        result = re.sub(r'\d+', '<NUM>', message)
        # Replace UUIDs
        result = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '<UUID>', result)
        # Replace hex strings
        result = re.sub(r'0x[a-f0-9]+', '<HEX>', result)
        # Replace IP addresses
        result = re.sub(r'\d+\.\d+\.\d+\.\d+', '<IP>', result)
        # Replace quoted strings
        result = re.sub(r'"[^"]*"', '<STR>', result)
        result = re.sub(r"'[^']*'", '<STR>', result)
        
        return result
    
    def _detect_level(self, message: str) -> str:
        """Detect log level from message content."""
        message_lower = message.lower()
        if any(word in message_lower for word in ["error", "exception", "failed", "fatal"]):
            return "error"
        elif any(word in message_lower for word in ["warn", "warning"]):
            return "warning"
        return "info"
    
    def _categorize_error(self, message: str) -> str:
        """Categorize an error message."""
        for pattern, category in self.ERROR_PATTERNS:
            if re.search(pattern, message):
                return category
        return "other"
