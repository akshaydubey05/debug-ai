"""
Docker Ingester - Ingest logs from Docker containers
"""

from typing import List, Dict, Any, Optional, Generator
from datetime import datetime


class DockerIngester:
    """
    Ingests logs from Docker containers.
    Supports fetching logs from running and stopped containers.
    """
    
    def __init__(self):
        self._client = None
        self._connected = False
    
    def _get_client(self):
        """Get or create Docker client."""
        if self._client is None:
            try:
                import docker
                self._client = docker.from_env()
                self._connected = True
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Docker: {e}")
        return self._client
    
    def ingest(
        self,
        container: str,
        tail: int = 1000,
        since: Optional[str] = None,
        until: Optional[str] = None,
        follow: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Ingest logs from a Docker container.
        
        Args:
            container: Container name or ID
            tail: Number of lines from end
            since: Start time (Unix timestamp or datetime)
            until: End time
            follow: Follow log output
        
        Returns:
            List of log entries
        """
        client = self._get_client()
        logs = []
        
        try:
            container_obj = client.containers.get(container)
            
            # Get container info
            info = container_obj.attrs
            service_name = info.get("Name", container).lstrip("/")
            image = info.get("Config", {}).get("Image", "unknown")
            
            # Fetch logs
            log_output = container_obj.logs(
                tail=tail,
                timestamps=True,
                since=since,
                until=until,
                stream=False,
            )
            
            # Parse logs
            for line in log_output.decode("utf-8", errors="replace").split("\n"):
                if not line.strip():
                    continue
                
                entry = self._parse_docker_log(line, service_name, image)
                logs.append(entry)
        
        except Exception as e:
            logs.append({
                "raw": f"Error fetching logs from {container}: {e}",
                "source": f"docker:{container}",
                "error": True,
                "level": "error",
            })
        
        return logs
    
    def ingest_multiple(
        self,
        containers: List[str],
        tail: int = 1000,
        since: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Ingest logs from multiple containers."""
        all_logs = []
        
        for container in containers:
            logs = self.ingest(container, tail=tail, since=since)
            all_logs.extend(logs)
        
        # Sort by timestamp
        all_logs.sort(key=lambda x: x.get("timestamp", ""))
        
        return all_logs
    
    def stream(
        self,
        container: str,
        since: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream logs from a container in real-time."""
        client = self._get_client()
        
        try:
            container_obj = client.containers.get(container)
            service_name = container_obj.attrs.get("Name", container).lstrip("/")
            image = container_obj.attrs.get("Config", {}).get("Image", "unknown")
            
            for line in container_obj.logs(
                stream=True,
                follow=True,
                timestamps=True,
                since=since,
            ):
                text = line.decode("utf-8", errors="replace").strip()
                if text:
                    yield self._parse_docker_log(text, service_name, image)
        
        except Exception as e:
            yield {
                "raw": f"Stream error: {e}",
                "source": f"docker:{container}",
                "error": True,
                "level": "error",
            }
    
    def list_containers(self, all: bool = False) -> List[Dict[str, Any]]:
        """List available containers."""
        client = self._get_client()
        containers = []
        
        for container in client.containers.list(all=all):
            containers.append({
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
            })
        
        return containers
    
    def _parse_docker_log(
        self,
        line: str,
        service_name: str,
        image: str
    ) -> Dict[str, Any]:
        """Parse a Docker log line."""
        entry = {
            "raw": line,
            "source": f"docker:{service_name}",
            "service": service_name,
            "image": image,
        }
        
        # Docker logs with timestamps: "2024-01-01T00:00:00.000000000Z message"
        if line and len(line) > 30 and line[4] == "-":
            try:
                timestamp_str = line[:30].strip()
                message = line[31:].strip()
                entry["timestamp"] = timestamp_str
                entry["message"] = message
                entry["raw"] = message
            except:
                entry["message"] = line
        else:
            entry["message"] = line
        
        # Detect level
        entry["level"] = self._detect_level(entry.get("message", line))
        
        return entry
    
    def _detect_level(self, message: str) -> str:
        """Detect log level from message."""
        msg_upper = message.upper()
        
        if any(word in msg_upper for word in ["ERROR", "FATAL", "CRITICAL", "EXCEPTION"]):
            return "error"
        elif any(word in msg_upper for word in ["WARN", "WARNING"]):
            return "warn"
        elif any(word in msg_upper for word in ["DEBUG", "TRACE"]):
            return "debug"
        
        return "info"
