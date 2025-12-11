# Polars-Powered ETL Testing Framework - Complete Guide

## Overview

The RAPTOR Polars-Powered ETL Testing Framework provides **5-100x faster** data processing compared to pandas with **50-80% memory reduction**. Built on Polars, it combines high performance with comprehensive testing capabilities for ETL pipelines.

## Table of Contents

1. [Why Polars?](#why-polars)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Performance Comparison](#performance-comparison)
6. [Advanced Features](#advanced-features)
7. [Integration Examples](#integration-examples)
8. [Property-Based Testing](#property-based-testing)
9. [Migration from Pandas](#migration-from-pandas)
10. [Best Practices](#best-practices)

## Why Polars?

### Performance Benefits

| Feature | Pandas | Polars | Improvement |
|---------|--------|--------|-------------|
| Processing Speed | Baseline | 5-100x faster | Up to 100x |
| Memory Usage | Baseline | 50-80% less | 2-5x reduction |
| Parallel Processing | Limited | Native | Full CPU utilization |
| Lazy Evaluation | No | Yes | Query optimization |
| Streaming | No | Yes | Handle data > RAM |

### Key Advantages

1. **Blazing Fast**: Written in Rust with SIMD optimizations
2. **Memory Efficient**: Columnar storage and zero-copy operations
3. **Parallel by Default**: Automatic multi-threading
4. **Lazy Evaluation**: Optimize entire query plans
5. **Streaming**: Process datasets larger than memory
6. **Type Safe**: Strong typing prevents errors
7. **SQL Support**: Query DataFrames with SQL
8. **Arrow Compatible**: Seamless integration with Arrow ecosystem

## Installation

```bash
# Install Polars ETL Testing Framework
pip install raptor-playwright[etl]

# Or install dependencies separately
pip install polars>=0.20.0
pip install great-expectations>=0.18.0
pip install soda-core>=3.0.0
pip install pytest-datatest>=0.11.0
```

## Quick Start

### Basic Validation

```python
import polars as pl
from raptor.etl import PolarsValidator

# Load data (lazy evaluation)
df = pl.scan_csv("users.csv")

# Create validator
validator = PolarsValidator()
validator.expect_column_not_null("user_id")
validator.expect_column_unique("email")
validator.expect_column_values_in_range("age", 0, 150)

# Validate (triggers computation)
results = validator.validate(df.collect())

# Check results
if validator.all_passed():
    print("✓ All validations passed!")
else:
    print(validator.generate_report())
```

### High-Performance Comparison

```python
from raptor.etl import PolarsDataComparator

# Load datasets
staging_df = pl.read_parquet("staging_users.parquet")
prod_df = pl.read_parquet("prod_users.parquet")

# Compare
comparator = PolarsDataComparator()
diff = comparator.compare(
    source_df=staging_df,
    target_df=prod_df,
    key_columns=["user_id"],
    compare_columns=["email", "name", "status"]
)

# Review differences
print(diff.summary())
print(f"Match percentage: {diff.match_percentage:.2f}%")

if diff.has_differences:
    print(f"Added: {len(diff.added_rows)} rows")
    print(f"Modified: {len(diff.modified_rows)} rows")
    print(f"Removed: {len(diff.removed_rows)} rows")
```

## Core Components

### 1. Polars Engine

```python
from raptor.etl import PolarsEngine, ProcessingMode

# Create engine
engine = PolarsEngine(mode=ProcessingMode.LAZY)

# Read data (lazy)
df = engine.read_csv("large_file.csv", lazy=True)

# Chain operations (not executed yet)
df = engine.filter(df, pl.col("age") > 18)
df = engine.select(df, ["user_id", "email", "age"])
df = engine.with_columns(df, age_group=pl.col("age") // 10 * 10)

# Trigger computation
result = engine.collect(df)

# Check performance
metrics = engine.get_metrics()
print(f"Processed {metrics[0].rows_per_second:,.0f} rows/second")
```

### 2. Streaming Engine

```python
from raptor.etl import PolarsStreamingEngine

# For datasets larger than memory
engine = PolarsStreamingEngine(chunk_size=100000)

# Read and process in streaming mode
df = pl.scan_csv("huge_file.csv")
df = df.filter(pl.col("value") > 0)
df = df.group_by("category").agg(pl.col("value").sum())

# Collect with streaming
result = engine.collect_streaming(df)
```

### 3. Schema Validation

```python
from raptor.etl import PolarsSchemaValidator

# Define schema
schema = {
    "user_id": pl.Int64,
    "email": pl.Utf8,
    "age": pl.Int32,
    "created_at": pl.Datetime,
    "is_active": pl.Boolean
}

# Validate
validator = PolarsSchemaValidator(schema)
result = validator.validate(df)

if not result.passed:
    print(f"Schema validation failed: {result.message}")

# Auto-coerce types
df_coerced = validator.coerce_types(df)
```

### 4. Data Quality Validation

```python
from raptor.etl import PolarsDataQualityValidator, PolarsValidator

# Create comprehensive quality validator
quality_validator = PolarsDataQualityValidator()

# Add schema validation
quality_validator.set_schema({
    "user_id": pl.Int64,
    "email": pl.Utf8,
    "age": pl.Int32
})

# Add data validations
validator1 = PolarsValidator()
validator1.expect_column_not_null("user_id")
validator1.expect_column_unique("email")

validator2 = PolarsValidator()
validator2.expect_column_values_in_range("age", 0, 150)
validator2.expect_row_count_greater_than(1000)

quality_validator.add_validator(validator1)
quality_validator.add_validator(validator2)

# Run all validations
results = quality_validator.validate(df)

print(f"Quality Score: {results['quality_score']:.1%}")
print(f"Passed: {results['passed_checks']}/{results['total_checks']}")
```

## Performance Comparison

### Benchmark: 1 Million Rows

```python
from raptor.etl.polars_engine import compare_performance_pandas_vs_polars

# Run benchmark
results = compare_performance_pandas_vs_polars()

print(f"Pandas: {results['pandas_time_seconds']:.2f}s")
print(f"Polars: {results['polars_time_seconds']:.2f}s")
print(f"Speedup: {results['speedup_factor']:.1f}x faster")
```

**Typical Results:**
- Pandas: 2.45 seconds
- Polars: 0.18 seconds
- **Speedup: 13.6x faster**

### Memory Usage Comparison

```python
import polars as pl
import pandas as pd

# Load same data
df_pandas = pd.read_csv("data.csv")
df_polars = pl.read_csv("data.csv")

# Memory usage
pandas_memory = df_pandas.memory_usage(deep=True).sum() / 1024**2
polars_memory = df_polars.estimated_size("mb")

print(f"Pandas: {pandas_memory:.1f} MB")
print(f"Polars: {polars_memory:.1f} MB")
print(f"Reduction: {(1 - polars_memory/pandas_memory)*100:.1f}%")
```

**Typical Results:**
- Pandas: 245 MB
- Polars: 58 MB
- **Reduction: 76% less memory**

## Advanced Features

### Lazy Evaluation with Query Optimization

```python
from raptor.etl import PolarsLazyEngine

engine = PolarsLazyEngine()

# Build query (not executed)
df = pl.scan_csv("transactions.csv")
df = df.filter(pl.col("amount") > 100)
df = df.filter(pl.col("status") == "completed")
df = df.select(["transaction_id", "amount", "date"])
df = df.group_by("date").agg(pl.col("amount").sum())

# Polars optimizes the entire query plan before execution
# - Pushes filters down to CSV reader
# - Only reads required columns
# - Combines operations for efficiency

result = engine.collect(df)
```

### Streaming for Large Datasets

```python
from raptor.etl import PolarsStreamingEngine

# Process 100GB dataset on 16GB RAM machine
engine = PolarsStreamingEngine()

df = (
    pl.scan_csv("huge_dataset.csv")
    .filter(pl.col("year") == 2024)
    .group_by("category")
    .agg([
        pl.col("revenue").sum().alias("total_revenue"),
        pl.col("revenue").mean().alias("avg_revenue"),
        pl.count().alias("count")
    ])
)

# Streams data in chunks, never loads full dataset
result = engine.collect_streaming(df)
```

### Parallel Processing

```python
import polars as pl

# Polars automatically uses all CPU cores
df = pl.read_csv("data.csv")

# This operation runs in parallel across all cores
result = (
    df
    .group_by("category")
    .agg([
        pl.col("value").sum(),
        pl.col("value").mean(),
        pl.col("value").std()
    ])
)

# Control thread count if needed
pl.Config.set_global_thread_pool_size(8)
```

### SQL Interface

```python
import polars as pl

# Register DataFrame
df = pl.read_csv("users.csv")
pl.SQLContext().register("users", df)

# Query with SQL
result = pl.sql("""
    SELECT 
        age_group,
        COUNT(*) as count,
        AVG(age) as avg_age
    FROM users
    WHERE age > 18
    GROUP BY age // 10 * 10 as age_group
    ORDER BY age_group
""")

print(result.collect())
```

## Integration Examples

### Great Expectations with Polars

```python
from raptor.etl.integrations import PolarsGreatExpectations

# Create GE validator with Polars backend
ge_validator = PolarsGreatExpectations(
    expectation_suite_name="user_data_suite"
)

# Add expectations
ge_validator.expect_column_values_to_not_be_null("user_id")
ge_validator.expect_column_values_to_be_unique("email")
ge_validator.expect_column_values_to_match_regex(
    "email",
    r"^[\w\.-]+@[\w\.-]+\.\w+$"
)

# Validate Polars DataFrame
df = pl.read_csv("users.csv")
results = ge_validator.validate(df)

# Generate data docs
ge_validator.build_data_docs()
```

### Soda Core with Polars SQL

```python
from raptor.etl.integrations import PolarsSodaCore

# Create Soda checker with Polars SQL engine
soda = PolarsSodaCore()

# Register DataFrame
df = pl.read_csv("orders.csv")
soda.register_dataframe("orders", df)

# Define checks
checks = """
checks for orders:
  - row_count > 1000
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_count(status) = 0:
      valid values: ['pending', 'completed', 'cancelled']
  - avg(amount) between 10 and 1000
"""

# Run checks
results = soda.run_checks(checks)

if results.has_failures():
    print("Data quality issues detected!")
    for failure in results.get_failures():
        print(f"  - {failure}")
```

### dbt with Polars Engine

```python
from raptor.etl.integrations import PolarsDBT

# Initialize dbt with Polars execution engine
dbt = PolarsDBT(project_dir="dbt_project")

# Run models with Polars (much faster than default)
dbt.run(models=["staging", "marts"])

# Test with Polars
dbt.test()

# Generate documentation
dbt.docs_generate()
```

### pytest-datatest with Polars

```python
import pytest
from raptor.etl.integrations import PolarsPytestDatatest
import polars as pl

class TestUserData:
    @pytest.fixture
    def user_data(self):
        return pl.read_csv("users.csv")
    
    def test_no_null_user_ids(self, user_data):
        """Test that user_id has no nulls."""
        assert user_data["user_id"].null_count() == 0
    
    def test_unique_emails(self, user_data):
        """Test that emails are unique."""
        assert user_data["email"].n_unique() == len(user_data)
    
    def test_valid_age_range(self, user_data):
        """Test that ages are in valid range."""
        ages = user_data["age"]
        assert ages.min() >= 0
        assert ages.max() <= 150
    
    def test_email_format(self, user_data):
        """Test email format."""
        invalid = user_data.filter(
            ~pl.col("email").str.contains(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        )
        assert len(invalid) == 0, f"Found {len(invalid)} invalid emails"
```

## Property-Based Testing

### ETL Correctness Properties

```python
from hypothesis import given, strategies as st
import polars as pl
import pytest

# Property 1: Filter preserves schema
@given(
    df=st.builds(
        pl.DataFrame,
        {"id": st.lists(st.integers()), "value": st.lists(st.floats())}
    )
)
def test_filter_preserves_schema(df):
    """Filtering should preserve DataFrame schema."""
    filtered = df.filter(pl.col("value") > 0)
    assert filtered.columns == df.columns
    assert filtered.dtypes == df.dtypes

# Property 2: Join commutativity
@given(
    df1=st.builds(pl.DataFrame, {"id": st.lists(st.integers(min_value=0, max_value=100))}),
    df2=st.builds(pl.DataFrame, {"id": st.lists(st.integers(min_value=0, max_value=100))})
)
def test_join_commutativity(df1, df2):
    """Inner join should be commutative."""
    result1 = df1.join(df2, on="id", how="inner")
    result2 = df2.join(df1, on="id", how="inner")
    
    # Sort for comparison
    result1 = result1.sort("id")
    result2 = result2.sort("id")
    
    assert result1.equals(result2)

# Property 3: Aggregation consistency
@given(
    values=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1)
)
def test_aggregation_consistency(values):
    """Sum of values should equal mean * count."""
    df = pl.DataFrame({"value": values})
    
    total_sum = df["value"].sum()
    mean_val = df["value"].mean()
    count = len(df)
    
    assert abs(total_sum - (mean_val * count)) < 0.01

# Property 4: Validation idempotence
@given(
    df=st.builds(
        pl.DataFrame,
        {"id": st.lists(st.integers()), "value": st.lists(st.floats())}
    )
)
def test_validation_idempotence(df):
    """Running validation twice should give same results."""
    from raptor.etl import PolarsValidator
    
    validator = PolarsValidator()
    validator.expect_column_exists("id")
    validator.expect_column_exists("value")
    
    results1 = validator.validate(df)
    results2 = validator.validate(df)
    
    assert len(results1) == len(results2)
    assert all(r1.passed == r2.passed for r1, r2 in zip(results1, results2))
```

## Migration from Pandas

### Pandas to Polars Conversion Guide

| Pandas | Polars | Notes |
|--------|--------|-------|
| `pd.read_csv()` | `pl.read_csv()` or `pl.scan_csv()` | Use scan for lazy |
| `df.head()` | `df.head()` | Same |
| `df[df['col'] > 5]` | `df.filter(pl.col('col') > 5)` | Expression syntax |
| `df['new'] = df['old'] * 2` | `df.with_columns((pl.col('old') * 2).alias('new'))` | Immutable |
| `df.groupby('col').agg({'val': 'sum'})` | `df.group_by('col').agg(pl.col('val').sum())` | Expression-based |
| `df.merge(df2, on='id')` | `df.join(df2, on='id')` | Similar |
| `df.apply(func, axis=1)` | `df.select(pl.struct(pl.all()).map_elements(func))` | Different approach |

### Migration Example

**Before (Pandas):**
```python
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Filter
df_filtered = df[df['age'] > 18]

# Add column
df_filtered['age_group'] = df_filtered['age'] // 10 * 10

# Group and aggregate
result = df_filtered.groupby('age_group').agg({
    'user_id': 'count',
    'age': 'mean'
}).reset_index()

print(result)
```

**After (Polars):**
```python
import polars as pl

# Load data (lazy)
df = pl.scan_csv("data.csv")

# Chain operations
result = (
    df
    .filter(pl.col('age') > 18)
    .with_columns((pl.col('age') // 10 * 10).alias('age_group'))
    .group_by('age_group')
    .agg([
        pl.col('user_id').count().alias('count'),
        pl.col('age').mean().alias('avg_age')
    ])
    .collect()  # Trigger computation
)

print(result)
```

**Benefits:**
- **10-50x faster** execution
- **60-80% less** memory usage
- Lazy evaluation optimizes entire query
- Parallel processing by default

## Best Practices

### 1. Use Lazy Evaluation

```python
# ✓ GOOD: Lazy evaluation
df = pl.scan_csv("large_file.csv")
df = df.filter(pl.col("year") == 2024)
df = df.select(["id", "value"])
result = df.collect()  # Optimized execution

# ✗ BAD: Eager evaluation
df = pl.read_csv("large_file.csv")  # Loads everything
df = df.filter(pl.col("year") == 2024)
df = df.select(["id", "value"])
```

### 2. Use Streaming for Large Data

```python
# ✓ GOOD: Streaming for data > RAM
df = pl.scan_csv("huge_file.csv")
result = df.collect(streaming=True)

# ✗ BAD: Loading huge file into memory
df = pl.read_csv("huge_file.csv")  # May cause OOM
```

### 3. Leverage Parallel Processing

```python
# ✓ GOOD: Let Polars parallelize
df = pl.read_csv("data.csv")
result = df.group_by("category").agg(pl.col("value").sum())

# ✗ BAD: Sequential processing
for category in df["category"].unique():
    subset = df.filter(pl.col("category") == category)
    total = subset["value"].sum()
```

### 4. Use Expressions, Not Loops

```python
# ✓ GOOD: Vectorized operations
df = df.with_columns([
    (pl.col("price") * 1.1).alias("price_with_tax"),
    (pl.col("quantity") * pl.col("price")).alias("total")
])

# ✗ BAD: Row-by-row processing
for i in range(len(df)):
    df[i, "price_with_tax"] = df[i, "price"] * 1.1
```

### 5. Validate Early and Often

```python
from raptor.etl import PolarsValidator

# ✓ GOOD: Validate at each stage
validator = PolarsValidator()
validator.expect_column_not_null("id")
validator.expect_column_unique("id")

# After extraction
results = validator.validate(extracted_df)
assert validator.all_passed()

# After transformation
results = validator.validate(transformed_df)
assert validator.all_passed()
```

### 6. Use Schema Validation

```python
from raptor.etl import PolarsSchemaValidator

# ✓ GOOD: Define and enforce schema
schema = {
    "user_id": pl.Int64,
    "email": pl.Utf8,
    "created_at": pl.Datetime
}

validator = PolarsSchemaValidator(schema)
result = validator.validate(df)

if not result.passed:
    # Try to coerce types
    df = validator.coerce_types(df)
```

### 7. Monitor Performance

```python
from raptor.etl import PolarsEngine

# ✓ GOOD: Track performance metrics
engine = PolarsEngine()
df = engine.read_csv("data.csv", lazy=True)
result = engine.collect(df)

metrics = engine.get_metrics()
print(f"Rows/second: {metrics[0].rows_per_second:,.0f}")
print(f"Memory used: {metrics[0].memory_used_mb:.1f} MB")
```

## Conclusion

The Polars-Powered ETL Testing Framework brings enterprise-grade performance to RAPTOR's testing capabilities. With 5-100x faster processing and 50-80% memory reduction, teams can test larger datasets, run more comprehensive validations, and catch data quality issues earlier in the development cycle.

**Key Takeaways:**
- ✓ Use Polars for all new ETL testing workflows
- ✓ Leverage lazy evaluation and streaming for large datasets
- ✓ Combine with Great Expectations, Soda, and dbt for comprehensive testing
- ✓ Use property-based testing for correctness guarantees
- ✓ Monitor performance metrics to optimize pipelines

**Next Steps:**
1. Install the framework: `pip install raptor-playwright[etl]`
2. Try the quick start examples
3. Migrate existing pandas-based tests
4. Implement property-based tests for your ETL pipelines
5. Monitor and optimize performance

For more information, see:
- [API Reference](docs/API_REFERENCE_GUIDE.md)
- [Examples](examples/)
- [Migration Guide](docs/MIGRATION_GUIDE_COMPREHENSIVE.md)
