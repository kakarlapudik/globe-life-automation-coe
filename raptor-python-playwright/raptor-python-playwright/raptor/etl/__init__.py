"""
RAPTOR ETL Testing Framework - Polars-Powered

High-performance ETL testing framework powered by Polars for 5-100x faster
data processing compared to pandas, with 50-80% memory reduction.

Key Features:
- Polars-based data processing engine (5-100x faster than pandas)
- Great Expectations with Polars backend
- Native Polars schema validation with type safety
- Soda Core with Polars SQL engine
- dbt integration with Polars execution engine
- pytest-datatest with Polars-aware assertions
- Streaming support for datasets larger than memory
- Lazy evaluation and parallel processing by default
- High-performance data comparison and diff utilities
- ETL pipeline testing with validation at each stage
- Data quality dashboard and reporting
- Property-based tests for ETL correctness

Performance:
- 5-100x faster than pandas
- 50-80% memory reduction
- Parallel processing by default
- Lazy evaluation for large datasets
- Streaming for datasets larger than memory

Example Usage:
    import polars as pl
    from raptor.etl import PolarsETLTester, PolarsValidator
    
    # Load data with Polars (lazy evaluation)
    df = pl.scan_csv("data.csv")
    
    # Create validator
    validator = PolarsValidator()
    validator.expect_column_not_null("user_id")
    validator.expect_column_unique("email")
    
    # Validate (triggers computation)
    result = validator.validate(df.collect())
    
    # High-performance comparison
    from raptor.etl.comparators import PolarsDataComparator
    comparator = PolarsDataComparator()
    diff = comparator.compare(source_df, target_df, key_columns=["id"])
"""

from raptor.etl.polars_engine import (
    PolarsEngine,
    PolarsLazyEngine,
    PolarsStreamingEngine
)
from raptor.etl.validators import (
    PolarsValidator,
    PolarsSchemaValidator,
    PolarsDataQualityValidator
)
from raptor.etl.comparators import (
    PolarsDataComparator,
    PolarsSchemaComparator,
    PolarsDiffEngine
)
from raptor.etl.integrations import (
    PolarsGreatExpectations,
    PolarsSodaCore,
    PolarsDBT,
    PolarsPytestDatatest
)
from raptor.etl.pipeline import (
    PolarsETLPipeline,
    PolarsETLTester,
    PolarsPipelineValidator
)
from raptor.etl.reporters import (
    PolarsDataQualityDashboard,
    PolarsTestReporter,
    PolarsCoverageReporter
)
from raptor.etl.models import (
    ValidationResult,
    TestStatus,
    QualityMetrics,
    PerformanceMetrics
)

__all__ = [
    # Core Engine
    'PolarsEngine',
    'PolarsLazyEngine',
    'PolarsStreamingEngine',
    
    # Validators
    'PolarsValidator',
    'PolarsSchemaValidator',
    'PolarsDataQualityValidator',
    
    # Comparators
    'PolarsDataComparator',
    'PolarsSchemaComparator',
    'PolarsDiffEngine',
    
    # Integrations
    'PolarsGreatExpectations',
    'PolarsSodaCore',
    'PolarsDBT',
    'PolarsPytestDatatest',
    
    # Pipeline
    'PolarsETLPipeline',
    'PolarsETLTester',
    'PolarsPipelineValidator',
    
    # Reporters
    'PolarsDataQualityDashboard',
    'PolarsTestReporter',
    'PolarsCoverageReporter',
    
    # Models
    'ValidationResult',
    'TestStatus',
    'QualityMetrics',
    'PerformanceMetrics',
]

__version__ = '2.0.0'
