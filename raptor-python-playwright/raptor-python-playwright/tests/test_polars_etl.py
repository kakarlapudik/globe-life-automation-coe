"""
Tests for Polars-powered ETL testing framework.

Demonstrates usage and validates correctness of ETL testing components.
"""

import pytest
import polars as pl
from raptor.etl import (
    PolarsEngine,
    PolarsValidator,
    PolarsSchemaValidator,
    PolarsDataComparator,
    ProcessingMode
)
from raptor.etl.validators import ValidationSeverity


class TestPolarsEngine:
    """Tests for Polars engine."""
    
    def test_engine_initialization(self):
        """Test engine can be initialized."""
        engine = PolarsEngine()
        assert engine.mode == ProcessingMode.LAZY
        assert engine.n_threads > 0
    
    def test_read_csv_lazy(self, tmp_path):
        """Test lazy CSV reading."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df.write_csv(csv_file)
        
        # Read lazily
        engine = PolarsEngine()
        lazy_df = engine.read_csv(csv_file, lazy=True)
        
        assert isinstance(lazy_df, pl.LazyFrame)
        
        # Collect and verify
        result = engine.collect(lazy_df)
        assert len(result) == 3
        assert result.columns == ["id", "value"]
    
    def test_filter_operation(self):
        """Test filter operation."""
        engine = PolarsEngine()
        df = pl.DataFrame({"id": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})
        
        filtered = engine.filter(df, pl.col("value") > 25)
        
        assert len(filtered) == 3
        assert filtered["value"].to_list() == [30, 40, 50]
    
    def test_performance_metrics(self, tmp_path):
        """Test performance metrics collection."""
        csv_file = tmp_path / "test.csv"
        df = pl.DataFrame({"id": range(1000), "value": range(1000)})
        df.write_csv(csv_file)
        
        engine = PolarsEngine()
        lazy_df = engine.read_csv(csv_file, lazy=True)
        result = engine.collect(lazy_df)
        
        metrics = engine.get_metrics()
        assert len(metrics) > 0
        assert metrics[0].rows_processed == 1000
        assert metrics[0].execution_time_seconds > 0


class TestPolarsValidator:
    """Tests for Polars validator."""
    
    def test_column_exists_validation(self):
        """Test column existence validation."""
        df = pl.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        
        validator = PolarsValidator()
        validator.expect_column_exists("id")
        validator.expect_column_exists("name")
        
        results = validator.validate(df)
        
        assert len(results) == 2
        assert all(r.passed for r in results)
    
    def test_column_not_null_validation(self):
        """Test not null validation."""
        df = pl.DataFrame({"id": [1, 2, None, 4], "value": [10, 20, 30, 40]})
        
        validator = PolarsValidator()
        validator.expect_column_not_null("id")
        validator.expect_column_not_null("value")
        
        results = validator.validate(df)
        
        assert len(results) == 2
        assert not results[0].passed  # id has null
        assert results[1].passed  # value has no nulls
        assert results[0].metadata["null_count"] == 1
    
    def test_column_unique_validation(self):
        """Test uniqueness validation."""
        df = pl.DataFrame({"id": [1, 2, 2, 3], "email": ["a@test.com", "b@test.com", "c@test.com", "d@test.com"]})
        
        validator = PolarsValidator()
        validator.expect_column_unique("id")
        validator.expect_column_unique("email")
        
        results = validator.validate(df)
        
        assert len(results) == 2
        assert not results[0].passed  # id has duplicates
        assert results[1].passed  # email is unique
    
    def test_column_values_in_range(self):
        """Test range validation."""
        df = pl.DataFrame({"age": [25, 30, 35, 200, 45]})
        
        validator = PolarsValidator()
        validator.expect_column_values_in_range("age", 0, 150)
        
        results = validator.validate(df)
        
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].metadata["violations"] == 1
    
    def test_column_values_match_regex(self):
        """Test regex pattern validation."""
        df = pl.DataFrame({
            "email": ["valid@test.com", "invalid", "also@valid.com", "bad_email"]
        })
        
        validator = PolarsValidator()
        validator.expect_column_values_match_regex("email", r"^[\w\.-]+@[\w\.-]+\.\w+$")
        
        results = validator.validate(df)
        
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].metadata["violations"] == 2
    
    def test_column_values_in_set(self):
        """Test value set validation."""
        df = pl.DataFrame({"status": ["active", "inactive", "pending", "invalid"]})
        
        validator = PolarsValidator()
        validator.expect_column_values_in_set("status", ["active", "inactive", "pending"])
        
        results = validator.validate(df)
        
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].metadata["violations"] == 1
    
    def test_row_count_validation(self):
        """Test row count validation."""
        df = pl.DataFrame({"id": range(500)})
        
        validator = PolarsValidator()
        validator.expect_row_count_greater_than(1000)
        
        results = validator.validate(df)
        
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].metadata["row_count"] == 500
    
    def test_validation_report(self):
        """Test validation report generation."""
        df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        
        validator = PolarsValidator()
        validator.expect_column_exists("id")
        validator.expect_column_not_null("id")
        validator.expect_column_unique("id")
        
        validator.validate(df)
        report = validator.generate_report()
        
        assert "VALIDATION REPORT" in report
        assert "Total Checks: 3" in report
        assert "Passed: 3" in report


class TestPolarsSchemaValidator:
    """Tests for schema validator."""
    
    def test_schema_validation_success(self):
        """Test successful schema validation."""
        df = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
            "age": [25, 30, 35]
        })
        
        schema = {
            "id": pl.Int64,
            "name": pl.Utf8,
            "age": pl.Int64
        }
        
        validator = PolarsSchemaValidator(schema)
        result = validator.validate(df)
        
        assert result.passed
        assert "Schema validation passed" in result.message
    
    def test_schema_validation_missing_columns(self):
        """Test schema validation with missing columns."""
        df = pl.DataFrame({"id": [1, 2, 3]})
        
        schema = {
            "id": pl.Int64,
            "name": pl.Utf8,
            "age": pl.Int64
        }
        
        validator = PolarsSchemaValidator(schema)
        result = validator.validate(df)
        
        assert not result.passed
        assert "Missing columns" in result.message
    
    def test_schema_validation_type_mismatch(self):
        """Test schema validation with type mismatch."""
        df = pl.DataFrame({
            "id": ["1", "2", "3"],  # String instead of Int
            "name": ["A", "B", "C"]
        })
        
        schema = {
            "id": pl.Int64,
            "name": pl.Utf8
        }
        
        validator = PolarsSchemaValidator(schema)
        result = validator.validate(df)
        
        assert not result.passed
        assert "expected" in result.message.lower()
    
    def test_type_coercion(self):
        """Test automatic type coercion."""
        df = pl.DataFrame({
            "id": ["1", "2", "3"],
            "value": ["10.5", "20.5", "30.5"]
        })
        
        schema = {
            "id": pl.Int64,
            "value": pl.Float64
        }
        
        validator = PolarsSchemaValidator(schema)
        coerced_df = validator.coerce_types(df)
        
        assert coerced_df["id"].dtype == pl.Int64
        assert coerced_df["value"].dtype == pl.Float64


class TestPolarsDataComparator:
    """Tests for data comparator."""
    
    def test_compare_identical_dataframes(self):
        """Test comparison of identical DataFrames."""
        df1 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        
        comparator = PolarsDataComparator()
        diff = comparator.compare(df1, df2, key_columns=["id"])
        
        assert not diff.has_differences
        assert diff.match_percentage == 100.0
        assert len(diff.added_rows) == 0
        assert len(diff.removed_rows) == 0
        assert len(diff.modified_rows) == 0
    
    def test_compare_added_rows(self):
        """Test detection of added rows."""
        df1 = pl.DataFrame({"id": [1, 2], "value": [10, 20]})
        df2 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        
        comparator = PolarsDataComparator()
        diff = comparator.compare(df1, df2, key_columns=["id"])
        
        assert diff.has_differences
        assert len(diff.added_rows) == 1
        assert diff.added_rows["id"].to_list() == [3]
    
    def test_compare_removed_rows(self):
        """Test detection of removed rows."""
        df1 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pl.DataFrame({"id": [1, 2], "value": [10, 20]})
        
        comparator = PolarsDataComparator()
        diff = comparator.compare(df1, df2, key_columns=["id"])
        
        assert diff.has_differences
        assert len(diff.removed_rows) == 1
        assert diff.removed_rows["id"].to_list() == [3]
    
    def test_compare_modified_rows(self):
        """Test detection of modified rows."""
        df1 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 25, 30]})
        
        comparator = PolarsDataComparator()
        diff = comparator.compare(df1, df2, key_columns=["id"], compare_columns=["value"])
        
        assert diff.has_differences
        assert len(diff.modified_rows) == 1
    
    def test_compare_schemas(self):
        """Test schema comparison."""
        df1 = pl.DataFrame({"id": [1, 2], "value": [10, 20]})
        df2 = pl.DataFrame({"id": [1, 2], "value": [10, 20], "extra": ["A", "B"]})
        
        comparator = PolarsDataComparator()
        schema_diff = comparator.compare_schemas(df1, df2)
        
        assert not schema_diff["schemas_match"]
        assert "extra" in schema_diff["added_columns"]
    
    def test_diff_summary(self):
        """Test diff summary generation."""
        df1 = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        df2 = pl.DataFrame({"id": [1, 2, 4], "value": [10, 25, 40]})
        
        comparator = PolarsDataComparator()
        diff = comparator.compare(df1, df2, key_columns=["id"])
        
        summary = diff.summary()
        
        assert "DATA COMPARISON SUMMARY" in summary
        assert "Source Rows: 3" in summary
        assert "Target Rows: 3" in summary


@pytest.mark.benchmark
class TestPerformance:
    """Performance benchmarks."""
    
    def test_large_dataset_validation(self, benchmark):
        """Benchmark validation on large dataset."""
        # Create large dataset
        df = pl.DataFrame({
            "id": range(100000),
            "value": range(100000),
            "category": ["A", "B", "C"] * 33334
        })
        
        validator = PolarsValidator()
        validator.expect_column_not_null("id")
        validator.expect_column_unique("id")
        validator.expect_column_values_in_set("category", ["A", "B", "C"])
        
        # Benchmark
        result = benchmark(validator.validate, df)
        
        assert validator.all_passed()
    
    def test_large_dataset_comparison(self, benchmark):
        """Benchmark comparison on large dataset."""
        # Create large datasets
        df1 = pl.DataFrame({
            "id": range(50000),
            "value": range(50000)
        })
        
        df2 = pl.DataFrame({
            "id": range(50000),
            "value": range(50000)
        })
        
        comparator = PolarsDataComparator()
        
        # Benchmark
        result = benchmark(
            comparator.compare,
            df1,
            df2,
            key_columns=["id"]
        )
        
        assert not result.has_differences


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
