"""
Data models for Polars ETL testing framework.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum
import polars as pl


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    message: str
    severity: str = "error"
    failed_rows: Optional[pl.DataFrame] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Data quality metrics."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    quality_score: float
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        return self.passed_checks / self.total_checks if self.total_checks > 0 else 0.0


@dataclass
class PerformanceMetrics:
    """Performance metrics for ETL operations."""
    execution_time_seconds: float
    memory_used_mb: float
    rows_processed: int
    processing_mode: str
    parallel_threads: int
    
    @property
    def rows_per_second(self) -> float:
        """Calculate processing throughput."""
        return self.rows_processed / self.execution_time_seconds if self.execution_time_seconds > 0 else 0
