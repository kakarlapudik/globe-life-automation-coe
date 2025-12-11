"""
Property-based tests for Polars ETL framework.

Tests correctness properties that should hold for all valid inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import polars as pl
from raptor.etl import (
    PolarsValidator,
    PolarsSchemaValidator,
    PolarsDataComparator
)


# Custom strategies for generating Polars DataFrames
@st.composite
def polars_dataframe(draw, columns=None, min_rows=0, max_rows=100):
    """Generate random Polars DataFrame."""
    if columns is None:
        # Generate random columns
        n_cols = draw(st.integers(min_value=1, max_value=5))
        columns = {f"col_{i}": st.integers() for i in range(n_cols)}
    
    n_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    
    data = {}
    for col_name, strategy in columns.items():
        data[col_name] = draw(st.lists(strategy, min_size=n_rows, max_size=n_rows))
    
    return pl.DataFrame(data)


class TestValidationProperties:
    """
    Property-based tests for validation correctness.
    
    Feature: polars-etl-testing, Property 1: Validation Idempotence
    Validates: Requirements ETL-001
    """
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "value": st.floats(allow_nan=False)},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_validation_idempotence(self, df):
        """
        Property 1: Validation Idempotence
        
        For any DataFrame, running the same validation twice should
        produce identical results.
        """
        validator = PolarsValidator()
        validator.expect_column_exists("id")
        validator.expect_column_exists("value")
        
        # Run validation twice
        results1 = validator.validate(df)
        validator.results.clear()  # Clear results
        results2 = validator.validate(df)
        
        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.passed == r2.passed
            assert r1.check_name == r2.check_name
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(min_value=0, max_value=1000)},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_null_count_consistency(self, df):
        """
        Property 2: Null Count Consistency
        
        For any DataFrame, the null count reported by validation should
        match the actual null count in the column.
        """
        validator = PolarsValidator()
        validator.expect_column_not_null("id")
        
        results = validator.validate(df)
        
        actual_null_count = df["id"].null_count()
        reported_null_count = results[0].metadata.get("null_count", 0)
        
        assert actual_null_count == reported_null_count
    
    @given(
        values=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=50)
    )
    @settings(max_examples=100)
    def test_range_validation_correctness(self, values):
        """
        Property 3: Range Validation Correctness
        
        For any list of values, range validation should correctly identify
        values outside the specified range.
        """
        df = pl.DataFrame({"value": values})
        
        min_val = 20
        max_val = 80
        
        validator = PolarsValidator()
        validator.expect_column_values_in_range("value", min_val, max_val)
        
        results = validator.validate(df)
        
        # Count actual violations
        actual_violations = sum(1 for v in values if v < min_val or v > max_val)
        reported_violations = results[0].metadata.get("violations", 0)
        
        assert actual_violations == reported_violations


class TestSchemaProperties:
    """
    Property-based tests for schema validation.
    
    Feature: polars-etl-testing, Property 4: Schema Validation Consistency
    Validates: Requirements ETL-002
    """
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "name": st.text()},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_schema_validation_consistency(self, df):
        """
        Property 4: Schema Validation Consistency
        
        For any DataFrame, if schema validation passes, the DataFrame
        should have exactly the columns and types specified in the schema.
        """
        # Get actual schema
        actual_schema = {col: dtype for col, dtype in zip(df.columns, df.dtypes)}
        
        validator = PolarsSchemaValidator(actual_schema)
        result = validator.validate(df)
        
        # Validation should always pass for matching schema
        assert result.passed
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "value": st.floats(allow_nan=False)},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_coercion_preserves_data(self, df):
        """
        Property 5: Type Coercion Preserves Data
        
        For any DataFrame, coercing to the same types should not change
        the data values (only potentially the representation).
        """
        original_schema = {col: dtype for col, dtype in zip(df.columns, df.dtypes)}
        
        validator = PolarsSchemaValidator(original_schema)
        coerced_df = validator.coerce_types(df)
        
        # Data should be equivalent
        assert df.equals(coerced_df)


class TestComparisonProperties:
    """
    Property-based tests for data comparison.
    
    Feature: polars-etl-testing, Property 6: Comparison Symmetry
    Validates: Requirements ETL-003
    """
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(min_value=0, max_value=100), "value": st.integers()},
            min_rows=1,
            max_rows=30
        )
    )
    @settings(max_examples=100)
    def test_comparison_reflexivity(self, df):
        """
        Property 6: Comparison Reflexivity
        
        For any DataFrame, comparing it with itself should show no differences.
        """
        comparator = PolarsDataComparator()
        diff = comparator.compare(df, df, key_columns=["id"])
        
        assert not diff.has_differences
        assert len(diff.added_rows) == 0
        assert len(diff.removed_rows) == 0
        assert len(diff.modified_rows) == 0
        assert diff.match_percentage == 100.0
    
    @given(
        df1=polars_dataframe(
            columns={"id": st.integers(min_value=0, max_value=50)},
            min_rows=1,
            max_rows=20
        ),
        df2=polars_dataframe(
            columns={"id": st.integers(min_value=0, max_value=50)},
            min_rows=1,
            max_rows=20
        )
    )
    @settings(max_examples=100)
    def test_comparison_symmetry(self, df1, df2):
        """
        Property 7: Comparison Symmetry
        
        For any two DataFrames, added rows in one direction should equal
        removed rows in the other direction.
        """
        comparator = PolarsDataComparator()
        
        diff1 = comparator.compare(df1, df2, key_columns=["id"])
        diff2 = comparator.compare(df2, df1, key_columns=["id"])
        
        # Added in df1->df2 should equal removed in df2->df1
        assert len(diff1.added_rows) == len(diff2.removed_rows)
        assert len(diff1.removed_rows) == len(diff2.added_rows)
    
    @given(
        ids=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=30, unique=True)
    )
    @settings(max_examples=100)
    def test_comparison_transitivity(self, ids):
        """
        Property 8: Comparison Transitivity
        
        If df1 == df2 and df2 == df3, then df1 == df3.
        """
        # Create three identical DataFrames
        df1 = pl.DataFrame({"id": ids, "value": ids})
        df2 = pl.DataFrame({"id": ids, "value": ids})
        df3 = pl.DataFrame({"id": ids, "value": ids})
        
        comparator = PolarsDataComparator()
        
        diff12 = comparator.compare(df1, df2, key_columns=["id"])
        diff23 = comparator.compare(df2, df3, key_columns=["id"])
        diff13 = comparator.compare(df1, df3, key_columns=["id"])
        
        # All should show no differences
        assert not diff12.has_differences
        assert not diff23.has_differences
        assert not diff13.has_differences


class TestFilterProperties:
    """
    Property-based tests for filtering operations.
    
    Feature: polars-etl-testing, Property 9: Filter Preserves Schema
    Validates: Requirements ETL-004
    """
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "value": st.integers()},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_filter_preserves_schema(self, df):
        """
        Property 9: Filter Preserves Schema
        
        For any DataFrame, filtering should preserve the schema
        (column names and types).
        """
        original_columns = df.columns
        original_dtypes = df.dtypes
        
        # Apply filter
        filtered = df.filter(pl.col("value") > 0)
        
        # Schema should be preserved
        assert filtered.columns == original_columns
        assert filtered.dtypes == original_dtypes
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "value": st.integers()},
            min_rows=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_filter_subset_property(self, df):
        """
        Property 10: Filter Produces Subset
        
        For any DataFrame, filtering should produce a subset
        (filtered rows <= original rows).
        """
        filtered = df.filter(pl.col("value") > 0)
        
        assert len(filtered) <= len(df)
    
    @given(
        df=polars_dataframe(
            columns={"id": st.integers(), "value": st.integers()},
            min_rows=1,
            max_rows=50
        )
    )
    @settings(max_examples=100)
    def test_filter_idempotence(self, df):
        """
        Property 11: Filter Idempotence
        
        For any DataFrame, applying the same filter twice should
        produce the same result as applying it once.
        """
        condition = pl.col("value") > 0
        
        filtered_once = df.filter(condition)
        filtered_twice = filtered_once.filter(condition)
        
        assert filtered_once.equals(filtered_twice)


class TestAggregationProperties:
    """
    Property-based tests for aggregation operations.
    
    Feature: polars-etl-testing, Property 12: Aggregation Consistency
    Validates: Requirements ETL-005
    """
    
    @given(
        values=st.lists(
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_sum_mean_consistency(self, values):
        """
        Property 12: Sum-Mean Consistency
        
        For any list of values, sum should equal mean * count.
        """
        df = pl.DataFrame({"value": values})
        
        total_sum = df["value"].sum()
        mean_val = df["value"].mean()
        count = len(df)
        
        # Allow small floating point error
        assert abs(total_sum - (mean_val * count)) < 0.01
    
    @given(
        values=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=50)
    )
    @settings(max_examples=100)
    def test_count_consistency(self, values):
        """
        Property 13: Count Consistency
        
        For any DataFrame, the count aggregation should equal
        the number of non-null values.
        """
        df = pl.DataFrame({"value": values})
        
        count_agg = df.select(pl.col("value").count()).item()
        actual_count = len([v for v in values if v is not None])
        
        assert count_agg == actual_count


class TestJoinProperties:
    """
    Property-based tests for join operations.
    
    Feature: polars-etl-testing, Property 14: Join Commutativity
    Validates: Requirements ETL-006
    """
    
    @given(
        ids1=st.lists(st.integers(min_value=0, max_value=50), min_size=1, max_size=20),
        ids2=st.lists(st.integers(min_value=0, max_value=50), min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    def test_inner_join_commutativity(self, ids1, ids2):
        """
        Property 14: Inner Join Commutativity
        
        For any two DataFrames, inner join should be commutative
        (order doesn't matter for the result set).
        """
        df1 = pl.DataFrame({"id": ids1, "value1": ids1})
        df2 = pl.DataFrame({"id": ids2, "value2": ids2})
        
        # Join in both directions
        result1 = df1.join(df2, on="id", how="inner").sort("id")
        result2 = df2.join(df1, on="id", how="inner").sort("id")
        
        # Should have same number of rows
        assert len(result1) == len(result2)
        
        # Should have same id values
        assert result1["id"].to_list() == result2["id"].to_list()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
