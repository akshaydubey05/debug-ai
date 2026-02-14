"""
Basic unit tests for DebugAI
"""
import pytest
from pathlib import Path


def test_package_import():
    """Test that the debugai package can be imported"""
    try:
        import debugai
        assert debugai is not None
    except ImportError as e:
        pytest.fail(f"Failed to import debugai: {e}")


def test_parser_import():
    """Test that the parser module can be imported"""
    try:
        from debugai.ingestion.parser import LogParser
        assert LogParser is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LogParser: {e}")


def test_analyzer_import():
    """Test that the analyzer module can be imported"""
    try:
        from debugai.core.analyzer import LogAnalyzer
        assert LogAnalyzer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LogAnalyzer: {e}")


def test_database_import():
    """Test that the database module can be imported"""
    try:
        from debugai.storage.database import Database
        assert Database is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Database: {e}")


def test_cli_import():
    """Test that the CLI module can be imported"""
    try:
        from debugai.cli.main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import CLI app: {e}")


def test_version():
    """Test that version is defined"""
    import debugai
    assert hasattr(debugai, '__version__')
    assert isinstance(debugai.__version__, str)
    assert len(debugai.__version__) > 0
