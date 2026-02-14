"""
Stress Test Suite for DebugAI
Tests performance under high load and concurrent operations
"""

import sys
import time
import random
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from debugai.ingestion.parser import LogParser
from debugai.core.analyzer import LogAnalyzer
from debugai.storage.database import Database


class StressTestRunner:
    """Run stress tests for DebugAI components"""
    
    def __init__(self):
        self.results = {}
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        self.temp_dir = tempfile.mkdtemp(prefix="debugai_stress_")
        print(f"   Temp directory: {self.temp_dir}")
        
    def teardown(self):
        """Cleanup test environment"""
        print("\n🧹 Cleaning up...")
        if self.temp_dir and Path(self.temp_dir).exists():
            try:
                # Give time for any file handles to close
                time.sleep(0.2)
                shutil.rmtree(self.temp_dir)
                print("   ✓ Cleanup complete")
            except Exception as e:
                print(f"   ⚠ Warning: Could not remove temp directory: {e}")
        
    def generate_log_entry(self, index: int, service: str = "api") -> Dict[str, Any]:
        """Generate realistic log entry as dictionary"""
        levels = ["INFO", "WARN", "ERROR", "DEBUG"]
        errors = [
            "Connection timeout to database",
            "NullPointerException in UserService",
            "Failed to authenticate user",
            "Out of memory error",
            "Database query timeout",
            "Network connection refused",
            "Invalid API key provided",
            "Rate limit exceeded",
        ]
        
        level = random.choice(levels)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
        
        if level == "ERROR":
            message = random.choice(errors)
        else:
            message = f"Processing request #{index}"
        
        raw_log = f"{timestamp.isoformat()} [{level}] [{service}] {message}"
        
        return {
            "raw": raw_log,
            "service": service,
            "timestamp": timestamp.isoformat()
        }
    
    def test_parser_throughput(self, log_count: int = 10000):
        """Test log parser throughput"""
        print(f"\n📊 Testing Parser Throughput ({log_count:,} logs)...")
        
        # Generate logs
        print("   Generating logs...")
        logs = [self.generate_log_entry(i) for i in range(log_count)]
        
        # Parse logs
        parser = LogParser()
        print("   Parsing logs...")
        start = time.time()
        
        parsed = []
        errors = 0
        for log in logs:
            try:
                result = parser.parse(log)
                if result:
                    parsed.append(result)
            except Exception as e:
                errors += 1
        
        duration = time.time() - start
        if duration == 0:
            duration = 0.001  # Prevent division by zero
        throughput = len(parsed) / duration
        
        print(f"   ✓ Parsed {len(parsed):,}/{log_count:,} logs in {duration:.2f}s")
        print(f"   ✓ Throughput: {throughput:,.0f} logs/sec")
        if errors > 0:
            print(f"   ⚠ Parse errors: {errors}")
        
        self.results['parser_throughput'] = throughput
        self.results['parsed_count'] = len(parsed)
        return throughput
    
    def test_analyzer_performance(self, log_count: int = 5000):
        """Test analyzer performance with large datasets"""
        print(f"\n📊 Testing Analyzer Performance ({log_count:,} logs)...")
        
        # Generate and parse logs
        print("   Generating logs...")
        services = ["api", "db", "redis", "cache"]
        logs = []
        
        for i in range(log_count):
            service = random.choice(services)
            log_data = self.generate_log_entry(i, service)
            
            # Create simpler log dict for analyzer
            logs.append({
                "timestamp": log_data["timestamp"],
                "level": random.choice(["INFO", "WARN", "ERROR", "DEBUG"]),
                "service": service,
                "message": log_data["raw"],
                "raw": log_data["raw"]
            })
        
        # Analyze logs
        analyzer = LogAnalyzer()
        print("   Analyzing logs...")
        start = time.time()
        
        try:
            results = analyzer.analyze(logs)
            duration = time.time() - start
            
            patterns = results.get('patterns', [])
            error_types = results.get('error_types', {})
            
            print(f"   ✓ Analyzed {len(logs):,} logs in {duration:.2f}s")
            print(f"   ✓ Found {len(patterns)} patterns")
            print(f"   ✓ Found {len(error_types)} error types")
            
            self.results['analyzer_duration'] = duration
            self.results['patterns_found'] = len(patterns)
        except Exception as e:
            print(f"   ⚠ Analyzer error: {e}")
            self.results['analyzer_duration'] = 0
    
    def test_database_operations(self, operation_count: int = 500):
        """Test database write/read performance"""
        print(f"\n📊 Testing Database Operations ({operation_count:,} ops)...")
        
        db_path = Path(self.temp_dir) / "test.db"
        
        try:
            db = Database(str(db_path))
            parser = LogParser()
            
            # Test writes
            print("   Testing writes...")
            stored_count = 0
            start = time.time()
            
            for i in range(operation_count):
                log_entry = self.generate_log_entry(i)
                try:
                    parsed = parser.parse(log_entry)
                    if parsed:
                        db.store_log(parsed, source_name=f"stress-test-{random.randint(1, 3)}")
                        stored_count += 1
                except Exception as e:
                    pass
            
            write_duration = time.time() - start
            if write_duration == 0:
                write_duration = 0.001
            write_throughput = stored_count / write_duration
            
            print(f"   ✓ Writes: {stored_count:,}/{operation_count:,} in {write_duration:.2f}s ({write_throughput:,.0f} ops/sec)")
            
            # Test reads
            if stored_count > 0:
                print("   Testing reads...")
                start = time.time()
                read_count = min(50, stored_count)
                for _ in range(read_count):
                    try:
                        results = db.get_logs(limit=10)
                    except:
                        pass
                read_duration = time.time() - start
                
                print(f"   ✓ Reads: {read_count} queries in {read_duration:.2f}s")
                self.results['db_read_duration'] = read_duration
            
            self.results['db_write_throughput'] = write_throughput
            self.results['stored_count'] = stored_count
            
            # Close database
            try:
                db.close()
            except:
                pass
            
            # Wait for cleanup
            time.sleep(0.1)
            
        except Exception as e:
            print(f"   ⚠ Database test error: {e}")
    
    def test_concurrent_parsing(self, thread_count: int = 5, logs_per_thread: int = 500):
        """Test concurrent log parsing"""
        print(f"\n📊 Testing Concurrent Parsing ({thread_count} threads, {logs_per_thread:,} logs each)...")
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def parse_logs(thread_id: int):
            """Parse logs in thread"""
            parser = LogParser()
            local_results = []
            local_errors = []
            
            for i in range(logs_per_thread):
                log_entry = self.generate_log_entry(i, f"service-{thread_id}")
                try:
                    parsed = parser.parse(log_entry)
                    if parsed:
                        local_results.append(parsed)
                except Exception as e:
                    local_errors.append(str(e))
            
            with lock:
                results.extend(local_results)
                errors.extend(local_errors)
        
        # Create and start threads
        threads = []
        start = time.time()
        
        for i in range(thread_count):
            thread = threading.Thread(target=parse_logs, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        duration = time.time() - start
        total_expected = thread_count * logs_per_thread
        if duration == 0:
            duration = 0.001
        throughput = len(results) / duration
        
        print(f"   ✓ Parsed {len(results):,}/{total_expected:,} logs in {duration:.2f}s")
        print(f"   ✓ Throughput: {throughput:,.0f} logs/sec")
        if errors:
            print(f"   ⚠ Errors: {len(errors)}")
        
        self.results['concurrent_throughput'] = throughput
        self.results['concurrent_parsed'] = len(results)
        
    def test_large_batch_processing(self, log_count: int = 20000):
        """Test processing large batches of logs"""
        print(f"\n📊 Testing Large Batch Processing ({log_count:,} logs)...")
        
        print("   Generating logs...")
        logs = []
        for i in range(log_count):
            logs.append(self.generate_log_entry(i, f"service-{i % 5}"))
        
        print("   Processing batch...")
        parser = LogParser()
        start = time.time()
        
        parsed = []
        for log in logs:
            try:
                result = parser.parse(log)
                if result:
                    parsed.append(result.to_dict())
            except:
                pass
        
        duration = time.time() - start
        if duration == 0:
            duration = 0.001
        
        # Calculate memory usage estimate
        import sys
        if parsed:
            memory_mb = sys.getsizeof(parsed) / (1024 * 1024)
            per_log_kb = (memory_mb / len(parsed)) * 1024
        else:
            memory_mb = 0
            per_log_kb = 0
        
        print(f"   ✓ Processed {len(parsed):,} logs in {duration:.2f}s")
        print(f"   ✓ Throughput: {len(parsed)/duration:,.0f} logs/sec")
        print(f"   ✓ Memory usage: ~{memory_mb:.2f} MB")
        if parsed:
            print(f"   ✓ Per log: ~{per_log_kb:.2f} KB")
        
        self.results['batch_throughput'] = len(parsed) / duration
        self.results['memory_mb'] = memory_mb
    
    def test_error_detection(self, log_count: int = 3000):
        """Test error detection and categorization"""
        print(f"\n📊 Testing Error Detection ({log_count:,} logs)...")
        
        # Generate logs with specific error patterns
        print("   Generating logs with errors...")
        logs = []
        error_count = 0
        
        for i in range(log_count):
            # 30% errors
            if random.random() < 0.3:
                level = "ERROR"
                error_count += 1
            else:
                level = random.choice(["INFO", "WARN", "DEBUG"])
            
            service = random.choice(["api", "db", "redis"])
            log_entry = self.generate_log_entry(i, service)
            
            logs.append({
                "timestamp": log_entry["timestamp"],
                "level": level,
                "service": service,
                "message": log_entry["raw"],
                "raw": log_entry["raw"]
            })
        
        print(f"   Generated {error_count} error logs")
        
        # Analyze
        analyzer = LogAnalyzer()
        start = time.time()
        
        try:
            results = analyzer.analyze(logs)
            duration = time.time() - start
            
            error_types = results.get('error_types', {})
            anomalies = results.get('anomalies', [])
            
            print(f"   ✓ Analyzed in {duration:.2f}s")
            print(f"   ✓ Error types detected: {len(error_types)}")
            print(f"   ✓ Anomalies found: {len(anomalies)}")
            
            self.results['error_detection_duration'] = duration
        except Exception as e:
            print(f"   ⚠ Error detection failed: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📈 STRESS TEST SUMMARY")
        print("="*60)
        
        if 'parser_throughput' in self.results:
            print(f"Parser Throughput:        {self.results['parser_throughput']:>15,.0f} logs/sec")
            print(f"  Parsed Successfully:    {self.results.get('parsed_count', 0):>15,} logs")
        
        if 'analyzer_duration' in self.results and self.results['analyzer_duration'] > 0:
            print(f"\nAnalyzer Performance:")
            print(f"  Duration:               {self.results['analyzer_duration']:>15.2f} seconds")
            print(f"  Patterns Found:         {self.results.get('patterns_found', 0):>15}")
        
        if 'db_write_throughput' in self.results:
            print(f"\nDatabase Performance:")
            print(f"  Write Throughput:       {self.results['db_write_throughput']:>15,.0f} ops/sec")
            print(f"  Records Stored:         {self.results.get('stored_count', 0):>15,}")
            if 'db_read_duration' in self.results:
                print(f"  Read Duration:          {self.results['db_read_duration']:>15.2f} seconds")
        
        if 'concurrent_throughput' in self.results:
            print(f"\nConcurrent Processing:")
            print(f"  Throughput:             {self.results['concurrent_throughput']:>15,.0f} logs/sec")
            print(f"  Parsed Successfully:    {self.results.get('concurrent_parsed', 0):>15,}")
        
        if 'batch_throughput' in self.results:
            print(f"\nBatch Processing:")
            print(f"  Throughput:             {self.results['batch_throughput']:>15,.0f} logs/sec")
            print(f"  Memory Usage:           {self.results.get('memory_mb', 0):>15.2f} MB")
        
        if 'error_detection_duration' in self.results:
            print(f"\nError Detection:")
            print(f"  Duration:               {self.results['error_detection_duration']:>15.2f} seconds")
        
        print("="*60)
        print("✅ All stress tests completed!")
        print("="*60)


def main():
    """Run all stress tests"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║          DebugAI Stress Test Suite                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    runner = StressTestRunner()
    
    try:
        runner.setup()
        
        # Run all tests
        runner.test_parser_throughput(log_count=10000)
        runner.test_analyzer_performance(log_count=5000)
        runner.test_database_operations(operation_count=500)
        runner.test_concurrent_parsing(thread_count=5, logs_per_thread=500)
        runner.test_large_batch_processing(log_count=20000)
        runner.test_error_detection(log_count=3000)
        
        # Print summary
        runner.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during stress test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        runner.teardown()


if __name__ == "__main__":
    main()
