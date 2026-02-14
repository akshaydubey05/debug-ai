"""
File Ingester - Ingest logs from files and directories
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import os
import gzip
import re
from datetime import datetime


class FileIngester:
    """
    Ingests log files from the filesystem.
    Supports plain text, gzipped files, and recursive directory scanning.
    """
    
    SUPPORTED_EXTENSIONS = {".log", ".txt", ".json", ".gz"}
    
    def __init__(self):
        self._file_count = 0
        self._line_count = 0
    
    def ingest(
        self,
        path: Path,
        services: Optional[List[str]] = None,
        levels: Optional[List[str]] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ingest logs from a file or directory.
        
        Args:
            path: Path to file or directory
            services: Filter by service names
            levels: Filter by log levels
            since: Start time filter
            until: End time filter
            pattern: Regex pattern to match
        
        Returns:
            List of raw log entries
        """
        logs = []
        
        if path.is_file():
            logs.extend(self._read_file(path))
        elif path.is_dir():
            logs.extend(self._read_directory(path))
        else:
            raise FileNotFoundError(f"Path not found: {path}")
        
        # Apply filters
        if services or levels or since or until or pattern:
            logs = self._filter_logs(logs, services, levels, since, until, pattern)
        
        return logs
    
    def ingest_streaming(
        self,
        path: Path,
        batch_size: int = 100
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Ingest logs in batches for memory efficiency."""
        batch = []
        
        for log in self._iter_file(path):
            batch.append(log)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch
    
    def _read_file(self, path: Path) -> List[Dict[str, Any]]:
        """Read a single log file."""
        logs = []
        
        try:
            if path.suffix == ".gz":
                with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
                    logs = self._parse_file_content(f, path)
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    logs = self._parse_file_content(f, path)
            
            self._file_count += 1
        except Exception as e:
            # Log error but continue
            logs.append({
                "raw": f"Error reading {path}: {e}",
                "source": str(path),
                "error": True
            })
        
        return logs
    
    def _read_directory(self, path: Path) -> List[Dict[str, Any]]:
        """Recursively read all log files in a directory."""
        logs = []
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                logs.extend(self._read_file(file_path))
        
        return logs
    
    def _iter_file(self, path: Path) -> Generator[Dict[str, Any], None, None]:
        """Iterate over lines in a file."""
        try:
            opener = gzip.open if path.suffix == ".gz" else open
            with opener(path, "rt", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        yield {
                            "raw": line,
                            "source": str(path),
                            "line_number": line_num,
                        }
        except Exception as e:
            yield {"raw": f"Error: {e}", "source": str(path), "error": True}
    
    def _parse_file_content(self, file_handle, path: Path) -> List[Dict[str, Any]]:
        """Parse content from a file handle."""
        logs = []
        service_name = self._detect_service_from_path(path)
        
        # Check if it's JSON logs (one JSON per line)
        first_line = file_handle.readline()
        file_handle.seek(0)
        
        is_json = first_line.strip().startswith("{")
        
        for line_num, line in enumerate(file_handle, 1):
            line = line.strip()
            if not line:
                continue
            
            self._line_count += 1
            
            entry = {
                "raw": line,
                "source": str(path),
                "line_number": line_num,
                "service": service_name,
            }
            
            # Try to extract timestamp
            timestamp = self._extract_timestamp(line)
            if timestamp:
                entry["timestamp"] = timestamp
            
            # Try to extract level
            level = self._extract_level(line)
            if level:
                entry["level"] = level
            
            logs.append(entry)
        
        return logs
    
    def _detect_service_from_path(self, path: Path) -> str:
        """Detect service name from file path."""
        # Try to extract service from filename like "api.log", "db-service.log"
        name = path.stem
        # Remove common suffixes
        for suffix in [".log", "-log", "_log", ".error", ".access"]:
            name = name.replace(suffix, "")
        return name or "unknown"
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        patterns = [
            r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",  # ISO format
            r"\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}",     # Apache format
            r"\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}",     # Syslog format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        
        return None
    
    def _extract_level(self, line: str) -> Optional[str]:
        """Extract log level from log line."""
        line_upper = line.upper()
        
        if any(word in line_upper for word in ["ERROR", "ERR", "FATAL", "CRITICAL"]):
            return "error"
        elif any(word in line_upper for word in ["WARN", "WARNING"]):
            return "warn"
        elif any(word in line_upper for word in ["INFO", "NOTICE"]):
            return "info"
        elif any(word in line_upper for word in ["DEBUG", "TRACE"]):
            return "debug"
        
        return None
    
    def _filter_logs(
        self,
        logs: List[Dict[str, Any]],
        services: Optional[List[str]],
        levels: Optional[List[str]],
        since: Optional[str],
        until: Optional[str],
        pattern: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Filter logs based on criteria."""
        filtered = logs
        
        if services:
            filtered = [l for l in filtered if l.get("service") in services]
        
        if levels:
            filtered = [l for l in filtered if l.get("level") in levels]
        
        if pattern:
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = [l for l in filtered if regex.search(l.get("raw", ""))]
        
        # Time filtering would require parsing timestamps
        # Simplified for now
        
        return filtered
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get ingestion statistics."""
        return {
            "files_processed": self._file_count,
            "lines_processed": self._line_count,
        }
