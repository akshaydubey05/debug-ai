"""
Error Correlator - Find relationships between errors across services
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import re


class ErrorCorrelator:
    """
    Correlates errors across services to find root causes.
    Uses temporal proximity, trace IDs, and semantic similarity.
    """
    
    def __init__(self, time_window: int = 60):
        """
        Initialize correlator.
        
        Args:
            time_window: Time window in seconds for correlation
        """
        self.time_window = time_window
    
    def correlate(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate errors and add correlation metadata.
        
        Args:
            errors: List of error entries
        
        Returns:
            Errors with correlation information added
        """
        if not errors:
            return errors
        
        # Group by trace ID if available
        trace_groups = self._group_by_trace_id(errors)
        
        # Group by time proximity
        time_groups = self._group_by_time(errors)
        
        # Find causal chains
        chains = self._find_causal_chains(errors)
        
        # Add correlation metadata to errors
        correlated = []
        for error in errors:
            error_copy = error.copy()
            error_copy["correlations"] = {
                "trace_group": trace_groups.get(error.get("error_id")),
                "time_group": time_groups.get(error.get("error_id")),
                "chain_position": chains.get(error.get("error_id")),
            }
            correlated.append(error_copy)
        
        # Sort by likely root cause first
        correlated.sort(key=lambda e: (
            e["correlations"].get("chain_position", 999),
            e.get("timestamp", "")
        ))
        
        return correlated
    
    def find_root_cause(self, errors: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Identify the most likely root cause error.
        
        Args:
            errors: List of error entries
        
        Returns:
            Most likely root cause error
        """
        if not errors:
            return None
        
        # Score each error
        scores = []
        for error in errors:
            score = self._calculate_root_cause_score(error, errors)
            scores.append((error, score))
        
        # Return highest scoring error
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0] if scores else None
    
    def group_related(self, errors: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group related errors together.
        
        Args:
            errors: List of error entries
        
        Returns:
            List of error groups
        """
        if not errors:
            return []
        
        # Use union-find for grouping
        parent = {i: i for i in range(len(errors))}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Connect related errors
        for i, error1 in enumerate(errors):
            for j, error2 in enumerate(errors[i+1:], i+1):
                if self._are_related(error1, error2):
                    union(i, j)
        
        # Group by parent
        groups = defaultdict(list)
        for i, error in enumerate(errors):
            groups[find(i)].append(error)
        
        return list(groups.values())
    
    def _group_by_trace_id(self, errors: List[Dict[str, Any]]) -> Dict[str, str]:
        """Group errors by trace ID."""
        trace_groups = {}
        trace_to_group = {}
        group_counter = 0
        
        for error in errors:
            trace_id = error.get("metadata", {}).get("trace_id")
            if trace_id:
                if trace_id not in trace_to_group:
                    trace_to_group[trace_id] = f"trace_{group_counter}"
                    group_counter += 1
                trace_groups[error.get("error_id")] = trace_to_group[trace_id]
        
        return trace_groups
    
    def _group_by_time(self, errors: List[Dict[str, Any]]) -> Dict[str, str]:
        """Group errors by temporal proximity."""
        time_groups = {}
        group_counter = 0
        
        # Sort by timestamp
        sorted_errors = sorted(errors, key=lambda e: e.get("timestamp", ""))
        
        current_group = None
        last_time = None
        
        for error in sorted_errors:
            timestamp_str = error.get("timestamp")
            if not timestamp_str:
                continue
            
            try:
                # Parse timestamp (simplified)
                current_time = self._parse_timestamp(timestamp_str)
                
                if last_time is None or (current_time - last_time).total_seconds() > self.time_window:
                    current_group = f"time_{group_counter}"
                    group_counter += 1
                
                time_groups[error.get("error_id")] = current_group
                last_time = current_time
            except:
                pass
        
        return time_groups
    
    def _find_causal_chains(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Find causal chains (which error caused which)."""
        chains = {}
        
        # Sort by timestamp
        sorted_errors = sorted(errors, key=lambda e: e.get("timestamp", ""))
        
        for i, error in enumerate(sorted_errors):
            chains[error.get("error_id")] = i
        
        return chains
    
    def _are_related(self, error1: Dict[str, Any], error2: Dict[str, Any]) -> bool:
        """Check if two errors are related."""
        # Same trace ID
        trace1 = error1.get("metadata", {}).get("trace_id")
        trace2 = error2.get("metadata", {}).get("trace_id")
        if trace1 and trace2 and trace1 == trace2:
            return True
        
        # Same request ID
        req1 = error1.get("metadata", {}).get("request_id")
        req2 = error2.get("metadata", {}).get("request_id")
        if req1 and req2 and req1 == req2:
            return True
        
        # Close in time
        try:
            time1 = self._parse_timestamp(error1.get("timestamp", ""))
            time2 = self._parse_timestamp(error2.get("timestamp", ""))
            if abs((time1 - time2).total_seconds()) < self.time_window:
                # Check if messages are similar
                msg1 = error1.get("message", "").lower()
                msg2 = error2.get("message", "").lower()
                
                # Simple similarity: shared words
                words1 = set(msg1.split())
                words2 = set(msg2.split())
                overlap = len(words1 & words2) / max(len(words1 | words2), 1)
                
                if overlap > 0.3:
                    return True
        except:
            pass
        
        return False
    
    def _calculate_root_cause_score(
        self,
        error: Dict[str, Any],
        all_errors: List[Dict[str, Any]]
    ) -> float:
        """Calculate how likely this error is the root cause."""
        score = 0.0
        
        # Earlier errors are more likely root causes
        try:
            timestamps = [self._parse_timestamp(e.get("timestamp", "")) for e in all_errors if e.get("timestamp")]
            error_time = self._parse_timestamp(error.get("timestamp", ""))
            if timestamps:
                min_time = min(timestamps)
                max_time = max(timestamps)
                time_range = (max_time - min_time).total_seconds() or 1
                position = (error_time - min_time).total_seconds() / time_range
                score += (1 - position) * 50  # Earlier = higher score
        except:
            pass
        
        # Lower-level services are more likely root causes
        service = error.get("service", "").lower()
        if any(db in service for db in ["db", "database", "postgres", "mysql", "redis", "mongo"]):
            score += 30
        elif any(infra in service for infra in ["queue", "kafka", "rabbit", "cache"]):
            score += 20
        
        # Certain error types suggest root cause
        message = error.get("message", "").lower()
        if any(term in message for term in ["connection refused", "timeout", "unavailable"]):
            score += 25
        
        return score
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime."""
        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        
        # Clean the string
        timestamp_str = timestamp_str[:19]  # Take first 19 chars
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except:
                continue
        
        return datetime.now()
