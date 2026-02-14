"""
Timeline Builder - Generate event timelines for debugging
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class TimelineBuilder:
    """
    Builds event timelines for debugging and incident analysis.
    """
    
    def __init__(self):
        self._events: List[Dict[str, Any]] = []
    
    def build(
        self,
        time_range: str = "5m",
        filter_level: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Build a timeline of events.
        
        Args:
            time_range: Time range (e.g., "5m", "1h", "1d")
            filter_level: Filter by level ("errors", "warnings", "all")
            service: Filter by service name
            limit: Maximum events to return
        
        Returns:
            List of timeline events
        """
        from debugai.storage.database import Database
        
        db = Database()
        
        # Parse time range
        since = self._parse_time_range(time_range)
        
        # Get events from database
        events = db.get_events(
            since=since,
            level=filter_level,
            service=service,
            limit=limit
        )
        
        # Sort by timestamp
        events.sort(key=lambda e: e.get("timestamp", ""))
        
        return events
    
    def trace_crash(
        self,
        error: Dict[str, Any],
        before: str = "5m"
    ) -> List[Dict[str, Any]]:
        """
        Trace events leading up to a crash/error.
        
        Args:
            error: The crash/error to trace back from
            before: How far back to look
        
        Returns:
            Timeline of events leading to the crash
        """
        from debugai.storage.database import Database
        
        db = Database()
        
        # Get error timestamp
        error_time = error.get("timestamp")
        if not error_time:
            return []
        
        # Parse time range
        time_delta = self._parse_time_delta(before)
        
        # Get events before the error
        events = db.get_events_before(
            timestamp=error_time,
            delta=time_delta,
            service=error.get("service")  # Focus on same service
        )
        
        # Add related events from other services
        trace_id = error.get("metadata", {}).get("trace_id")
        if trace_id:
            related = db.get_events_by_trace(trace_id)
            events.extend(related)
        
        # Deduplicate and sort
        seen = set()
        unique_events = []
        for event in events:
            event_id = event.get("error_id") or event.get("message", "")[:50]
            if event_id not in seen:
                seen.add(event_id)
                unique_events.append(event)
        
        unique_events.sort(key=lambda e: e.get("timestamp", ""))
        
        return unique_events
    
    def build_incident_timeline(
        self,
        errors: List[Dict[str, Any]],
        window: str = "10m"
    ) -> Dict[str, Any]:
        """
        Build a comprehensive incident timeline from multiple errors.
        
        Args:
            errors: List of related errors
            window: Time window around errors to include
        
        Returns:
            Incident timeline with analysis
        """
        if not errors:
            return {"events": [], "analysis": {}}
        
        # Find time range
        timestamps = [e.get("timestamp", "") for e in errors if e.get("timestamp")]
        if not timestamps:
            return {"events": errors, "analysis": {}}
        
        timestamps.sort()
        start_time = timestamps[0]
        end_time = timestamps[-1]
        
        # Build timeline
        timeline = []
        
        # Add errors
        for error in errors:
            timeline.append({
                "timestamp": error.get("timestamp"),
                "type": "error",
                "level": error.get("level", "error"),
                "service": error.get("service", "unknown"),
                "message": error.get("message", ""),
                "is_error": True
            })
        
        # Sort timeline
        timeline.sort(key=lambda e: e.get("timestamp", ""))
        
        # Analyze the timeline
        analysis = self._analyze_timeline(timeline)
        
        return {
            "start": start_time,
            "end": end_time,
            "duration": self._calculate_duration(start_time, end_time),
            "events": timeline,
            "analysis": analysis
        }
    
    def _parse_time_range(self, time_range: str) -> datetime:
        """Parse time range string and return start datetime."""
        delta = self._parse_time_delta(time_range)
        return datetime.now() - delta
    
    def _parse_time_delta(self, time_str: str) -> timedelta:
        """Parse time string to timedelta."""
        time_str = time_str.lower().strip()
        
        # Extract number and unit
        import re
        match = re.match(r"(\d+)\s*([mhds])", time_str)
        if not match:
            return timedelta(minutes=5)  # Default
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        elif unit == "s":
            return timedelta(seconds=value)
        
        return timedelta(minutes=5)
    
    def _calculate_duration(self, start: str, end: str) -> str:
        """Calculate duration between two timestamps."""
        try:
            start_dt = datetime.fromisoformat(start[:19])
            end_dt = datetime.fromisoformat(end[:19])
            delta = end_dt - start_dt
            
            seconds = int(delta.total_seconds())
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                return f"{seconds // 60}m {seconds % 60}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        except:
            return "unknown"
    
    def _analyze_timeline(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a timeline for patterns."""
        analysis = {
            "total_events": len(events),
            "error_count": 0,
            "services_affected": set(),
            "first_error": None,
            "cascade_detected": False
        }
        
        for event in events:
            if event.get("level") in ("error", "critical"):
                analysis["error_count"] += 1
                if analysis["first_error"] is None:
                    analysis["first_error"] = event
            
            service = event.get("service")
            if service:
                analysis["services_affected"].add(service)
        
        analysis["services_affected"] = list(analysis["services_affected"])
        
        # Detect cascade (errors in multiple services)
        if len(analysis["services_affected"]) > 1:
            analysis["cascade_detected"] = True
        
        return analysis
