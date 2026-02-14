"""
Database - SQLite storage for logs and analysis data
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import json
import os


class Database:
    """
    SQLite database for storing logs, errors, and analysis results.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database.
        
        Args:
            db_path: Path to database file (default: .debugai/debugai.db)
        """
        if db_path is None:
            debugai_dir = Path.cwd() / ".debugai"
            debugai_dir.mkdir(exist_ok=True)
            db_path = str(debugai_dir / "debugai.db")
        
        self.db_path = db_path
        self._connection = None
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Log sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                pattern TEXT DEFAULT '*.log',
                service TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Errors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id TEXT UNIQUE,
                level TEXT,
                service TEXT,
                message TEXT,
                raw TEXT,
                timestamp TEXT,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Events table (for timeline)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE,
                type TEXT,
                level TEXT,
                service TEXT,
                message TEXT,
                timestamp TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE,
                result TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON errors(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_service ON errors(service)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
        
        conn.commit()
    
    # Log Sources
    def add_log_source(
        self,
        name: str,
        path: str,
        pattern: str = "*.log",
        service: Optional[str] = None
    ) -> None:
        """Add a log source."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO log_sources (name, path, pattern, service)
            VALUES (?, ?, ?, ?)
        """, (name, path, pattern, service))
        
        conn.commit()
    
    def get_log_sources(self) -> List[Dict[str, Any]]:
        """Get all log sources."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM log_sources ORDER BY name")
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def remove_log_source(self, name: str) -> None:
        """Remove a log source."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM log_sources WHERE name = ?", (name,))
        conn.commit()
    
    # Errors
    def save_error(self, error: Dict[str, Any]) -> None:
        """Save an error to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO errors 
            (error_id, level, service, message, raw, timestamp, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            error.get("error_id"),
            error.get("level"),
            error.get("service"),
            error.get("message"),
            error.get("raw"),
            error.get("timestamp"),
            error.get("source"),
            json.dumps(error.get("metadata", {}))
        ))
        
        conn.commit()
    
    def save_errors(self, errors: List[Dict[str, Any]]) -> None:
        """Save multiple errors."""
        for error in errors:
            self.save_error(error)
    
    def get_error(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get an error by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM errors WHERE error_id = ?", (error_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result["metadata"] = json.loads(result.get("metadata", "{}"))
            return result
        
        return None
    
    def get_recent_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent errors."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM errors 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["metadata"] = json.loads(result.get("metadata", "{}"))
            results.append(result)
        
        return results
    
    # Events
    def save_event(self, event: Dict[str, Any]) -> None:
        """Save an event."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO events 
            (event_id, type, level, service, message, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("event_id"),
            event.get("type"),
            event.get("level"),
            event.get("service"),
            event.get("message"),
            event.get("timestamp"),
            json.dumps(event.get("metadata", {}))
        ))
        
        conn.commit()
    
    def get_events(
        self,
        since: Optional[datetime] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events with filters."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        
        if level:
            if level == "errors":
                query += " AND level IN ('error', 'critical', 'fatal')"
            elif level == "warnings":
                query += " AND level IN ('warn', 'warning')"
        
        if service:
            query += " AND service = ?"
            params.append(service)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_events_before(
        self,
        timestamp: str,
        delta: timedelta,
        service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events before a timestamp."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            end_time = datetime.fromisoformat(timestamp[:19])
            start_time = end_time - delta
        except:
            return []
        
        query = "SELECT * FROM events WHERE timestamp >= ? AND timestamp <= ?"
        params = [start_time.isoformat(), timestamp]
        
        if service:
            query += " AND service = ?"
            params.append(service)
        
        query += " ORDER BY timestamp"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_events_by_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get events with a specific trace ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM events 
            WHERE metadata LIKE ?
            ORDER BY timestamp
        """, (f'%"trace_id": "{trace_id}"%',))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Cache
    def cache_set(self, key: str, value: Any, ttl_hours: int = 24) -> None:
        """Set a cache value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        cursor.execute("""
            INSERT OR REPLACE INTO analysis_cache (cache_key, result, expires_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), expires_at.isoformat()))
        
        conn.commit()
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get a cache value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT result FROM analysis_cache 
            WHERE cache_key = ? AND expires_at > ?
        """, (key, datetime.now().isoformat()))
        
        row = cursor.fetchone()
        if row:
            return json.loads(row["result"])
        
        return None
    
    def cache_clear(self) -> None:
        """Clear expired cache entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM analysis_cache WHERE expires_at < ?
        """, (datetime.now().isoformat(),))
        
        conn.commit()
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
