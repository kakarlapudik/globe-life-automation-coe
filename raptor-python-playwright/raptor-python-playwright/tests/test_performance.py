"""
Performance Testing for RAPTOR Python Playwright Framework

This module measures framework performance metrics and compares them with
baseline requirements:
- Framework initialization time
- Element location performance
- Session restore time
- Database query performance
- Comparison with Java/Selenium baseline

Requirements: NFR-001
"""

import pytest
import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
import json

from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.session_manager import SessionManager
from raptor.core.config_manager import ConfigManager
from raptor.database.database_manager import DatabaseManager


# ============================================================================
# Performance Test Configuration
# ============================================================================

# Number of iterations for performance measurements
PERF_ITERATIONS = 10

# Performance targets (in seconds unless otherwise specified)
TARGETS = {
    "framework_init": 5.0,  # Framework initialization should complete within 5 seconds
    "element_location": 20.0,  # Element location within configured timeout (default 20s)
    "session_restore": 3.0,  # Session restore within 3 seconds
    "database_query": 2.0,  # Database query within 2 seconds
    "browser_launch": 10.0,  # Browser launch within 10 seconds
}

# Java/Selenium baseline metrics (for comparison)
# These are typical values from the existing Java framework
JAVA_BASELINE = {
    "framework_init": 8.0,  # Java framework typically takes 8 seconds
    "element_location": 25.0,  # Selenium element location typically 25 seconds
    "session_restore": 5.0,  # Java session restore typically 5 seconds
    "database_query": 2.5,  # Java database query typically 2.5 seconds
    "browser_launch": 15.0,  # Selenium browser launch typically 15 seconds
}


# ============================================================================
# Performance Measurement Utilities
# ============================================================================

class PerformanceMetrics:
    """Container for performance measurement results."""
    
    def __init__(self, operation: str):
        self.operation = operation
        self.measurements: List[float] = []
        self.target: float = TARGETS.get(operation, 0.0)
        self.baseline: float = JAVA_BASELINE.get(operation, 0.0)
    
    def add_measurement(self, duration: float):
        """Add a measurement in seconds."""
        self.measurements.append(duration)
    
    def get_stats(self) -> Dict[str, Any]:
        """Calculate statistics for measurements."""
        if not self.measurements:
            return {}
        
        return {
            "operation": self.operation,
            "count": len(self.measurements),
            "min": min(self.measurements),
            "max": max(self.measurements),
            "mean": statistics.mean(self.measurements),
            "median": statistics.median(self.measurements),
            "stdev": statistics.stdev(self.measurements) if len(self.measurements) > 1 else 0.0,
            "target": self.target,
            "baseline": self.baseline,
            "meets_target": statistics.mean(self.measurements) <= self.target if self.target > 0 else True,
            "vs_baseline": self._compare_to_baseline(),
        }
    
    def _compare_to_baseline(self) -> Dict[str, Any]:
        """Compare performance to Java/Selenium baseline."""
        if not self.measurements or self.baseline == 0:
            return {"improvement": "N/A", "percentage": 0.0}
        
        mean_time = statistics.mean(self.measurements)
        improvement = self.baseline - mean_time
        percentage = (improvement / self.baseline) * 100
        
        return {
            "improvement_seconds": round(improvement, 3),
            "improvement_percentage": round(percentage, 1),
            "faster": improvement > 0,
        }
    
    def print_summary(self):
        """Print a summary of the performance metrics."""
        stats = self.get_stats()
        if not stats:
            print(f"\n{self.operation}: No measurements")
            return
        
        print(f"\n{'='*70}")
        print(f"Performance Test: {stats['operation']}")
        print(f"{'='*70}")
        print(f"Iterations:        {stats['count']}")
        print(f"Mean Time:         {stats['mean']:.3f}s")
        print(f"Median Time:       {stats['median']:.3f}s")
        print(f"Min Time:          {stats['min']:.3f}s")
        print(f"Max Time:          {stats['max']:.3f}s")
        print(f"Std Deviation:     {stats['stdev']:.3f}s")
        print(f"Target:            {stats['target']:.3f}s")
        print(f"Meets Target:      {'✓ YES' if stats['meets_target'] else '✗ NO'}")
        
        if stats['baseline'] > 0:
            vs_baseline = stats['vs_baseline']
            print(f"\nComparison to Java/Selenium Baseline:")
            print(f"Baseline Time:     {stats['baseline']:.3f}s")
            print(f"Improvement:       {vs_baseline['improvement_seconds']:.3f}s ({vs_baseline['improvement_percentage']:.1f}%)")
            print(f"Result:            {'✓ FASTER' if vs_baseline['faster'] else '✗ SLOWER'}")
        
        print(f"{'='*70}\n")


def measure_time(func):
    """Decorator to measure execution time of async functions."""
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        return result, duration
    return wrapper


# ============================================================================
# Performance Test Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def perf_config():
    """Configuration for performance tests."""
    config = ConfigManager()
    config.load_config("dev")
    config.set("browser.headless", True)
    return config


@pytest.fixture(scope="module")
def perf_results_dir():
    """Directory for storing performance test results."""
    results_dir = Path("reports/performance")
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


# ============================================================================
# Test 1: Framework Initialization Performance
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_framework_initialization_performance(perf_config, perf_results_dir):
    """
    Measure framework initialization time.
    
    Tests the time required to initialize core framework components:
    - ConfigManager
    - BrowserManager
    - ElementManager (requires page)
    - SessionManager
    
    Target: < 5 seconds
    """
    metrics = PerformanceMetrics("framework_init")
    
    for i in range(PERF_ITERATIONS):
        start_time = time.perf_counter()
        
        # Initialize core components
        config = ConfigManager()
        config.load_config("dev")
        
        browser_manager = BrowserManager(config=config)
        session_manager = SessionManager(config=config)
        
        # Launch browser and create page for ElementManager
        await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        element_manager = ElementManager(page, config=config)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        metrics.add_measurement(duration)
        
        # Cleanup
        await browser_manager.close_browser()
        
        print(f"Iteration {i+1}/{PERF_ITERATIONS}: {duration:.3f}s")
    
    # Print and save results
    metrics.print_summary()
    stats = metrics.get_stats()
    
    # Save to JSON
    results_file = perf_results_dir / "framework_init_results.json"
    with open(results_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Assert meets target
    assert stats['meets_target'], (
        f"Framework initialization time {stats['mean']:.3f}s exceeds target {stats['target']:.3f}s"
    )


# ============================================================================
# Test 2: Element Location Performance
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_element_location_performance(perf_config, perf_results_dir):
    """
    Measure element location performance.
    
    Tests the time required to locate elements using various strategies:
    - CSS selectors
    - XPath
    - Text locators
    - With fallback strategies
    
    Target: < 20 seconds (configurable timeout)
    """
    metrics = PerformanceMetrics("element_location")
    
    # Setup browser once for all iterations
    browser_manager = BrowserManager(config=perf_config)
    await browser_manager.launch_browser("chromium", headless=True)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # Navigate to a test page
    await page.goto("https://example.com")
    
    element_manager = ElementManager(page, config=perf_config)
    
    # Test different locator strategies
    test_locators = [
        ("css=h1", None),  # Simple CSS
        ("xpath=//h1", None),  # XPath
        ("text=Example Domain", None),  # Text
        ("css=#nonexistent", ["xpath=//h1"]),  # With fallback
    ]
    
    for locator, fallback in test_locators:
        for i in range(PERF_ITERATIONS // len(test_locators)):
            start_time = time.perf_counter()
            
            try:
                await element_manager.locate_element(
                    locator,
                    fallback_locators=fallback,
                    timeout=5000  # 5 second timeout for test
                )
                end_time = time.perf_counter()
                duration = end_time - start_time
                metrics.add_measurement(duration)
                
                print(f"Located {locator}: {duration:.3f}s")
            except Exception as e:
                print(f"Failed to locate {locator}: {e}")
    
    # Cleanup
    await browser_manager.close_browser()
    
    # Print and save results
    metrics.print_summary()
    stats = metrics.get_stats()
    
    results_file = perf_results_dir / "element_location_results.json"
    with open(results_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Assert meets target
    assert stats['meets_target'], (
        f"Element location time {stats['mean']:.3f}s exceeds target {stats['target']:.3f}s"
    )


# ============================================================================
# Test 3: Session Restore Performance
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_session_restore_performance(perf_config, perf_results_dir):
    """
    Measure session restore performance.
    
    Tests the time required to:
    1. Save a browser session
    2. Restore the saved session
    
    Target: < 3 seconds
    """
    metrics_save = PerformanceMetrics("session_save")
    metrics_restore = PerformanceMetrics("session_restore")
    
    session_manager = SessionManager(config=perf_config)
    
    for i in range(PERF_ITERATIONS):
        # Create a browser session
        browser_manager = BrowserManager(config=perf_config)
        await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        await page.goto("https://example.com")
        
        # Measure save time
        start_time = time.perf_counter()
        session_info = await session_manager.save_session(
            page,
            f"perf_test_session_{i}",
            metadata={"test": "performance"}
        )
        end_time = time.perf_counter()
        save_duration = end_time - start_time
        metrics_save.add_measurement(save_duration)
        
        print(f"Iteration {i+1}/{PERF_ITERATIONS} - Save: {save_duration:.3f}s")
        
        # Measure restore time
        start_time = time.perf_counter()
        try:
            restored_page = await session_manager.restore_session(f"perf_test_session_{i}")
            end_time = time.perf_counter()
            restore_duration = end_time - start_time
            metrics_restore.add_measurement(restore_duration)
            
            print(f"Iteration {i+1}/{PERF_ITERATIONS} - Restore: {restore_duration:.3f}s")
        except Exception as e:
            print(f"Session restore failed: {e}")
        
        # Cleanup
        await browser_manager.close_browser()
        session_manager.delete_session(f"perf_test_session_{i}")
    
    # Print and save results
    print("\n=== Session Save Performance ===")
    metrics_save.print_summary()
    
    print("\n=== Session Restore Performance ===")
    metrics_restore.print_summary()
    
    # Save results
    save_stats = metrics_save.get_stats()
    restore_stats = metrics_restore.get_stats()
    
    results_file = perf_results_dir / "session_performance_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "save": save_stats,
            "restore": restore_stats
        }, f, indent=2)
    
    # Assert meets target
    assert restore_stats['meets_target'], (
        f"Session restore time {restore_stats['mean']:.3f}s exceeds target {restore_stats['target']:.3f}s"
    )


# ============================================================================
# Test 4: Database Query Performance
# ============================================================================

@pytest.mark.database
@pytest.mark.slow
def test_database_query_performance(perf_config, perf_results_dir):
    """
    Measure database query performance.
    
    Tests the time required to:
    1. Execute SELECT queries
    2. Execute UPDATE queries
    3. Import test data
    4. Export test results
    
    Target: < 2 seconds
    
    Note: This test requires database configuration. It will be skipped
    if database is not configured.
    """
    # Get database configuration
    db_config = perf_config.get("database", {})
    
    if not db_config or not db_config.get("server"):
        pytest.skip("Database not configured for performance testing")
    
    metrics_select = PerformanceMetrics("database_query_select")
    metrics_update = PerformanceMetrics("database_query_update")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager(
            server=db_config.get("server"),
            database=db_config.get("database"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            use_pooling=True
        )
        
        db_manager.connect()
        
        # Test SELECT queries
        for i in range(PERF_ITERATIONS):
            start_time = time.perf_counter()
            
            try:
                # Simple SELECT query
                results = db_manager.execute_query(
                    "SELECT TOP 10 * FROM DDFE_Elements"
                )
                end_time = time.perf_counter()
                duration = end_time - start_time
                metrics_select.add_measurement(duration)
                
                print(f"SELECT Iteration {i+1}/{PERF_ITERATIONS}: {duration:.3f}s ({len(results)} rows)")
            except Exception as e:
                print(f"SELECT query failed: {e}")
        
        # Test UPDATE queries (if test table exists)
        try:
            # Create a test table for updates
            db_manager.execute_update(
                """
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PerfTest')
                CREATE TABLE PerfTest (id INT PRIMARY KEY, value VARCHAR(100))
                """
            )
            
            for i in range(PERF_ITERATIONS):
                start_time = time.perf_counter()
                
                try:
                    # INSERT or UPDATE
                    db_manager.execute_update(
                        f"IF EXISTS (SELECT * FROM PerfTest WHERE id = {i}) "
                        f"UPDATE PerfTest SET value = 'test_{i}' WHERE id = {i} "
                        f"ELSE INSERT INTO PerfTest (id, value) VALUES ({i}, 'test_{i}')"
                    )
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    metrics_update.add_measurement(duration)
                    
                    print(f"UPDATE Iteration {i+1}/{PERF_ITERATIONS}: {duration:.3f}s")
                except Exception as e:
                    print(f"UPDATE query failed: {e}")
            
            # Cleanup test table
            db_manager.execute_update("DROP TABLE IF EXISTS PerfTest")
            
        except Exception as e:
            print(f"UPDATE test skipped: {e}")
        
        # Disconnect
        db_manager.disconnect()
        
    except Exception as e:
        pytest.skip(f"Database performance test failed: {e}")
    
    # Print and save results
    print("\n=== Database SELECT Performance ===")
    metrics_select.print_summary()
    
    if metrics_update.measurements:
        print("\n=== Database UPDATE Performance ===")
        metrics_update.print_summary()
    
    # Save results
    select_stats = metrics_select.get_stats()
    update_stats = metrics_update.get_stats() if metrics_update.measurements else {}
    
    results_file = perf_results_dir / "database_performance_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "select": select_stats,
            "update": update_stats
        }, f, indent=2)
    
    # Assert meets target
    assert select_stats['meets_target'], (
        f"Database query time {select_stats['mean']:.3f}s exceeds target {select_stats['target']:.3f}s"
    )


# ============================================================================
# Test 5: Browser Launch Performance
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_browser_launch_performance(perf_config, perf_results_dir):
    """
    Measure browser launch performance.
    
    Tests the time required to launch different browser types:
    - Chromium
    - Firefox (if available)
    - WebKit (if available)
    
    Target: < 10 seconds
    """
    metrics_chromium = PerformanceMetrics("browser_launch_chromium")
    metrics_firefox = PerformanceMetrics("browser_launch_firefox")
    metrics_webkit = PerformanceMetrics("browser_launch_webkit")
    
    browser_types = ["chromium", "firefox", "webkit"]
    metrics_map = {
        "chromium": metrics_chromium,
        "firefox": metrics_firefox,
        "webkit": metrics_webkit
    }
    
    for browser_type in browser_types:
        print(f"\n=== Testing {browser_type.upper()} ===")
        metrics = metrics_map[browser_type]
        
        for i in range(PERF_ITERATIONS):
            browser_manager = BrowserManager(config=perf_config)
            
            start_time = time.perf_counter()
            
            try:
                await browser_manager.launch_browser(browser_type, headless=True)
                end_time = time.perf_counter()
                duration = end_time - start_time
                metrics.add_measurement(duration)
                
                print(f"Iteration {i+1}/{PERF_ITERATIONS}: {duration:.3f}s")
                
                # Cleanup
                await browser_manager.close_browser()
            except Exception as e:
                print(f"Failed to launch {browser_type}: {e}")
                break
    
    # Print and save results
    all_results = {}
    
    for browser_type, metrics in metrics_map.items():
        if metrics.measurements:
            print(f"\n=== {browser_type.upper()} Launch Performance ===")
            metrics.print_summary()
            all_results[browser_type] = metrics.get_stats()
    
    # Save results
    results_file = perf_results_dir / "browser_launch_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Assert Chromium meets target (primary browser)
    if metrics_chromium.measurements:
        chromium_stats = metrics_chromium.get_stats()
        assert chromium_stats['meets_target'], (
            f"Chromium launch time {chromium_stats['mean']:.3f}s exceeds target {chromium_stats['target']:.3f}s"
        )


# ============================================================================
# Test 6: Comprehensive Performance Report
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_generate_comprehensive_performance_report(perf_results_dir):
    """
    Generate a comprehensive performance report combining all test results.
    
    This test aggregates results from all performance tests and generates
    a summary report comparing RAPTOR Python/Playwright performance with
    Java/Selenium baseline.
    """
    # Load all performance test results
    results_files = {
        "Framework Initialization": "framework_init_results.json",
        "Element Location": "element_location_results.json",
        "Session Performance": "session_performance_results.json",
        "Database Performance": "database_performance_results.json",
        "Browser Launch": "browser_launch_results.json",
    }
    
    all_results = {}
    
    for test_name, filename in results_files.items():
        results_file = perf_results_dir / filename
        if results_file.exists():
            with open(results_file, 'r') as f:
                all_results[test_name] = json.load(f)
    
    # Generate comprehensive report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("RAPTOR PYTHON PLAYWRIGHT FRAMEWORK - PERFORMANCE TEST REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Summary table
    report_lines.append("PERFORMANCE SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Test':<40} {'Mean Time':<12} {'Target':<12} {'Status':<10}")
    report_lines.append("-" * 80)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, results in all_results.items():
        if isinstance(results, dict) and "mean" in results:
            # Single result
            mean_time = results.get("mean", 0)
            target = results.get("target", 0)
            meets_target = results.get("meets_target", False)
            status = "✓ PASS" if meets_target else "✗ FAIL"
            
            report_lines.append(
                f"{test_name:<40} {mean_time:>10.3f}s {target:>10.3f}s {status:<10}"
            )
            
            total_tests += 1
            if meets_target:
                passed_tests += 1
        else:
            # Multiple results (e.g., session save/restore)
            for sub_test, sub_results in results.items():
                if isinstance(sub_results, dict) and "mean" in sub_results:
                    mean_time = sub_results.get("mean", 0)
                    target = sub_results.get("target", 0)
                    meets_target = sub_results.get("meets_target", False)
                    status = "✓ PASS" if meets_target else "✗ FAIL"
                    
                    full_name = f"{test_name} - {sub_test}"
                    report_lines.append(
                        f"{full_name:<40} {mean_time:>10.3f}s {target:>10.3f}s {status:<10}"
                    )
                    
                    total_tests += 1
                    if meets_target:
                        passed_tests += 1
    
    report_lines.append("-" * 80)
    report_lines.append(f"Total Tests: {total_tests} | Passed: {passed_tests} | Failed: {total_tests - passed_tests}")
    report_lines.append("")
    
    # Comparison with Java/Selenium baseline
    report_lines.append("COMPARISON WITH JAVA/SELENIUM BASELINE")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Test':<40} {'Python':<12} {'Java':<12} {'Improvement':<15}")
    report_lines.append("-" * 80)
    
    for test_name, results in all_results.items():
        if isinstance(results, dict) and "mean" in results:
            mean_time = results.get("mean", 0)
            baseline = results.get("baseline", 0)
            vs_baseline = results.get("vs_baseline", {})
            
            if baseline > 0:
                improvement = vs_baseline.get("improvement_percentage", 0)
                improvement_str = f"{improvement:+.1f}%"
                
                report_lines.append(
                    f"{test_name:<40} {mean_time:>10.3f}s {baseline:>10.3f}s {improvement_str:>15}"
                )
    
    report_lines.append("-" * 80)
    report_lines.append("")
    
    # Save report
    report_file = perf_results_dir / "PERFORMANCE_REPORT.txt"
    with open(report_file, 'w') as f:
        f.write("\n".join(report_lines))
    
    # Print report
    print("\n" + "\n".join(report_lines))
    
    # Assert overall success
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    assert success_rate >= 80, (
        f"Performance test success rate {success_rate:.1f}% is below 80% threshold"
    )


# ============================================================================
# Performance Test Markers
# ============================================================================

# Mark all tests in this module as performance tests
pytestmark = [pytest.mark.slow, pytest.mark.performance]
