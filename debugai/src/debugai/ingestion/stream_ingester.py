"""
Stream Ingester - Ingest logs from streams (stdin, files, URLs)
"""

from typing import List, Dict, Any, Optional, Generator
import sys
import time


class StreamIngester:
    """
    Ingests logs from streaming sources.
    Supports stdin, file tailing, and HTTP streams.
    """
    
    def __init__(self):
        self._buffer = []
    
    def stream(
        self,
        source: str,
        buffer_size: int = 100,
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Stream logs from a source.
        
        Args:
            source: Source type ("stdin", file path, or URL)
            buffer_size: Lines to buffer before yielding
        
        Yields:
            Batches of log entries
        """
        if source == "stdin":
            yield from self._stream_stdin(buffer_size)
        elif source.startswith("http://") or source.startswith("https://"):
            yield from self._stream_http(source, buffer_size)
        else:
            yield from self._stream_file(source, buffer_size)
    
    def _stream_stdin(
        self,
        buffer_size: int
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Stream from stdin."""
        buffer = []
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    buffer.append(self._parse_line(line, "stdin"))
                
                if len(buffer) >= buffer_size:
                    yield buffer
                    buffer = []
        except KeyboardInterrupt:
            pass
        
        if buffer:
            yield buffer
    
    def _stream_file(
        self,
        path: str,
        buffer_size: int
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Stream from a file (tail -f style)."""
        buffer = []
        
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    
                    if line:
                        line = line.strip()
                        if line:
                            buffer.append(self._parse_line(line, path))
                        
                        if len(buffer) >= buffer_size:
                            yield buffer
                            buffer = []
                    else:
                        if buffer:
                            yield buffer
                            buffer = []
                        time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        if buffer:
            yield buffer
    
    def _stream_http(
        self,
        url: str,
        buffer_size: int
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Stream from HTTP endpoint."""
        import httpx
        
        buffer = []
        
        try:
            with httpx.stream("GET", url) as response:
                for line in response.iter_lines():
                    if line:
                        buffer.append(self._parse_line(line, url))
                    
                    if len(buffer) >= buffer_size:
                        yield buffer
                        buffer = []
        except Exception as e:
            buffer.append({
                "raw": f"Stream error: {e}",
                "source": url,
                "level": "error",
                "error": True,
            })
        
        if buffer:
            yield buffer
    
    def watch(
        self,
        source_name: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Watch configured log sources for new entries."""
        from debugai.storage.database import Database
        
        db = Database()
        sources = db.get_log_sources()
        
        if source_name:
            sources = [s for s in sources if s["name"] == source_name]
        
        if not sources:
            return
        
        # Use watchdog for file monitoring
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class LogHandler(FileSystemEventHandler):
                def __init__(self, callback):
                    self.callback = callback
                    self._file_positions = {}
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    
                    path = event.src_path
                    pos = self._file_positions.get(path, 0)
                    
                    try:
                        with open(path, "r") as f:
                            f.seek(pos)
                            for line in f:
                                self.callback(line.strip(), path)
                            self._file_positions[path] = f.tell()
                    except:
                        pass
            
            entries = []
            
            def callback(line, path):
                entry = self._parse_line(line, path)
                entries.append(entry)
            
            observer = Observer()
            handler = LogHandler(callback)
            
            for source in sources:
                observer.schedule(handler, source["path"], recursive=True)
            
            observer.start()
            
            try:
                while True:
                    while entries:
                        yield entries.pop(0)
                    time.sleep(0.1)
            except KeyboardInterrupt:
                observer.stop()
            
            observer.join()
        
        except ImportError:
            # Fallback without watchdog
            while True:
                time.sleep(1)
    
    def _parse_line(self, line: str, source: str) -> Dict[str, Any]:
        """Parse a single log line."""
        entry = {
            "raw": line,
            "source": source,
            "message": line,
        }
        
        # Detect level
        line_upper = line.upper()
        if "ERROR" in line_upper or "FATAL" in line_upper:
            entry["level"] = "error"
        elif "WARN" in line_upper:
            entry["level"] = "warn"
        elif "DEBUG" in line_upper:
            entry["level"] = "debug"
        else:
            entry["level"] = "info"
        
        return entry
