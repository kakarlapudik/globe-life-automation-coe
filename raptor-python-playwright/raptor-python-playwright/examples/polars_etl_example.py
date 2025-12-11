"""
Comprehensive example of Polars-powered ETL testing.

Demonstrates real-world usage of the framework for ETL pipeline testing.
"""

import polars as pl
from raptor.etl import (
    PolarsEngine,
    PolarsValidator,
    PolarsSchemaValidator,
    PolarsDataQualityValidator,
    PolarsDataComparator,
    ProcessingMode
)


def example_1_basic_validation():
    """Example 1: Basic data validation."""
    print("\n" + "="*60)
    print("Example 1: Basic Data Validation")
    print("="*60)
    
    # Create sample data
    df = pl.DataFrame({
        "user_id": [1, 2, 3, 4, 5],
        "email": ["user1@test.com", "user2@test.com", "invalid", "user4@test.com", "user5@test.com"],
        "age": [25, 30, 35, 200, 45],
        "status": ["active", "active", "inactive", "active", "invalid_status"]
    })
    
    print("\nSample Data:")
    print(df)
    
    # Create validator
    validator = PolarsValidator()
    validator.expect_column_not_null("user_id")
    validator.expect_column_unique("user_id")
    validator.expect_column_values_match_regex("email", r"^[\w\.-]+@[\w\.-]+\.\w+$")
    validator.expect_column_values_in_range("age", 0, 150)
    validator.expect_column_values_in_set("status", ["active", "inactive", "pending"])
    
    # Validate
    results = validator.validate(df)
    
    # Print results
    print("\nValidation Results:")
    print(validator.generate_report())
    
    # Show failed validations
    if not validator.all_passed():
        print("\nFailed Validations:")
        for result in validator.get_failed_validations():
            print(f"  - {result.check_name}: {result.message}")
            if result.failed_rows is not None and len(result.failed_rows) > 0:
                print(f"    Failed rows: {len(result.failed_rows)}")


def example_2_schema_validation():
    """Example 2: Schema validation and type coercion."""
    print("\n" + "="*60)
    print("Example 2: Schema Validation")
    print("="*60)
    
    # Create data with mixed types
    df = pl.DataFrame({
        "user_id": ["1", "2", "3"],  # String instead of Int
        "email": ["user1@test.com", "user2@test.com", "user3@test.com"],
        "age": ["25", "30", "35"],  # String instead of Int
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"]
    })
    
    print("\nOriginal Data (with type issues):")
    print(df)
    print(f"\nOriginal Schema: {dict(zip(df.columns, df.dtypes))}")
    
    # Define expected schema
    schema = {
        "user_id": pl.Int64,
        "email": pl.Utf8,
        "age": pl.Int32,
        "created_at": pl.Date
    }
    
    # Validate schema
    validator = PolarsSchemaValidator(schema)
    result = validator.validate(df)
    
    print(f"\nSchema Validation: {'PASSED' if result.passed else 'FAILED'}")
    print(f"Message: {result.message}")
    
    # Coerce types
    if not result.passed:
        print("\nAttempting type coercion...")
        df_coerced = validator.coerce_types(df)
        print(f"Coerced Schema: {dict(zip(df_coerced.columns, df_coerced.dtypes))}")
        
        # Validate again
        result = validator.validate(df_coerced)
        print(f"Validation after coercion: {'PASSED' if result.passed else 'FAILED'}")


def example_3_data_comparison():
    """Example 3: High-performance data comparison."""
    print("\n" + "="*60)
    print("Example 3: Data Comparison")
    print("="*60)
    
    # Create staging data
    staging_df = pl.DataFrame({
        "user_id": [1, 2, 3, 4, 5],
        "email": ["user1@test.com", "user2@test.com", "user3@test.com", "user4@test.com", "user5@test.com"],
        "status": ["active", "active", "inactive", "active", "pending"]
    })
    
    # Create production data (with some differences)
    production_df = pl.DataFrame({
        "user_id": [1, 2, 3, 6],  # User 4 and 5 removed, user 6 added
        "email": ["user1@test.com", "user2_updated@test.com", "user3@test.com", "user6@test.com"],  # User 2 email changed
        "status": ["active", "active", "active", "active"]  # User 3 status changed
    })
    
    print("\nStaging Data:")
    print(staging_df)
    
    print("\nProduction Data:")
    print(production_df)
    
    # Compare
    comparator = PolarsDataComparator()
    diff = comparator.compare(
        source_df=staging_df,
        target_df=production_df,
        key_columns=["user_id"],
        compare_columns=["email", "status"]
    )
    
    # Print summary
    print(diff.summary())
    
    # Show details
    if diff.has_differences:
        if len(diff.added_rows) > 0:
            print("\nAdded Rows:")
            print(diff.added_rows)
        
        if len(diff.removed_rows) > 0:
            print("\nRemoved Rows:")
            print(diff.removed_rows)
        
        if len(diff.modified_rows) > 0:
            print("\nModified Rows:")
            print(diff.modified_rows.select(["user_id", "email", "email_target", "status", "status_target"]))


def example_4_comprehensive_quality_check():
    """Example 4: Comprehensive data quality validation."""
    print("\n" + "="*60)
    print("Example 4: Comprehensive Data Quality Check")
    print("="*60)
    
    # Create sample data
    df = pl.DataFrame({
        "user_id": [1, 2, 3, 4, 5],
        "email": ["user1@test.com", "user2@test.com", "user3@test.com", "user4@test.com", "user5@test.com"],
        "age": [25, 30, 35, 40, 45],
        "status": ["active", "active", "inactive", "active", "pending"],
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    })
    
    print("\nSample Data:")
    print(df)
    
    # Create comprehensive quality validator
    quality_validator = PolarsDataQualityValidator()
    
    # Set schema
    quality_validator.set_schema({
        "user_id": pl.Int64,
        "email": pl.Utf8,
        "age": pl.Int64,
        "status": pl.Utf8,
        "created_at": pl.Utf8
    })
    
    # Add data validations
    validator1 = PolarsValidator()
    validator1.expect_column_not_null("user_id")
    validator1.expect_column_unique("user_id")
    validator1.expect_column_not_null("email")
    validator1.expect_column_unique("email")
    
    validator2 = PolarsValidator()
    validator2.expect_column_values_in_range("age", 0, 150)
    validator2.expect_column_mean_in_range("age", 20, 60)
    validator2.expect_column_values_in_set("status", ["active", "inactive", "pending"])
    validator2.expect_row_count_greater_than(1)
    
    quality_validator.add_validator(validator1)
    quality_validator.add_validator(validator2)
    
    # Run all validations
    results = quality_validator.validate(df)
    
    # Print results
    print(f"\n{'='*60}")
    print("DATA QUALITY REPORT")
    print(f"{'='*60}")
    print(f"Total Checks: {results['total_checks']}")
    print(f"Passed: {results['passed_checks']} ({results['quality_score']:.1%})")
    print(f"Failed: {results['failed_checks']}")
    print(f"Overall Status: {'✓ PASSED' if results['all_passed'] else '✗ FAILED'}")
    print(f"{'='*60}")
    
    # Show individual results
    print("\nDetailed Results:")
    for result in results['results']:
        status = "✓" if result.passed else "✗"
        print(f"  {status} {result.check_name}: {result.message}")


def example_5_lazy_evaluation_performance():
    """Example 5: Lazy evaluation for performance."""
    print("\n" + "="*60)
    print("Example 5: Lazy Evaluation Performance")
    print("="*60)
    
    # Create engine with lazy mode
    engine = PolarsEngine(mode=ProcessingMode.LAZY)
    
    # Create large dataset
    print("\nCreating large dataset (1 million rows)...")
    large_df = pl.DataFrame({
        "id": range(1_000_000),
        "value": range(1_000_000),
        "category": ["A", "B", "C"] * 333334
    })
    
    # Save to CSV
    large_df.write_csv("temp_large_data.csv")
    
    # Read lazily (doesn't load data yet)
    print("Reading data lazily...")
    lazy_df = engine.read_csv("temp_large_data.csv", lazy=True)
    
    # Chain operations (still not executed)
    print("Building query plan...")
    lazy_df = engine.filter(lazy_df, pl.col("value") > 500000)
    lazy_df = engine.select(lazy_df, ["id", "value", "category"])
    lazy_df = engine.with_columns(lazy_df, value_squared=pl.col("value") ** 2)
    
    # Trigger computation
    print("Executing optimized query...")
    result = engine.collect(lazy_df)
    
    # Get metrics
    metrics = engine.get_metrics()
    
    print(f"\nResults:")
    print(f"  Rows processed: {metrics[0].rows_processed:,}")
    print(f"  Execution time: {metrics[0].execution_time_seconds:.3f} seconds")
    print(f"  Throughput: {metrics[0].rows_per_second:,.0f} rows/second")
    print(f"  Memory used: {metrics[0].memory_used_mb:.1f} MB")
    
    # Clean up
    import os
    os.remove("temp_large_data.csv")


def example_6_etl_pipeline_testing():
    """Example 6: Complete ETL pipeline testing."""
    print("\n" + "="*60)
    print("Example 6: ETL Pipeline Testing")
    print("="*60)
    
    # Simulate ETL pipeline stages
    
    # Stage 1: Extract
    print("\nStage 1: Extract")
    raw_data = pl.DataFrame({
        "user_id": ["1", "2", "3", "4", "5"],
        "email": ["USER1@TEST.COM", "user2@test.com", "user3@test.com", "invalid", "user5@test.com"],
        "age": ["25", "30", "35", "40", "45"],
        "status": ["ACTIVE", "active", "INACTIVE", "active", "pending"]
    })
    print(raw_data)
    
    # Validate extraction
    validator = PolarsValidator()
    validator.expect_row_count_greater_than(0)
    validator.expect_column_exists("user_id")
    validator.expect_column_exists("email")
    results = validator.validate(raw_data)
    print(f"Extraction validation: {'✓ PASSED' if validator.all_passed() else '✗ FAILED'}")
    
    # Stage 2: Transform
    print("\nStage 2: Transform")
    transformed_data = raw_data.with_columns([
        pl.col("user_id").cast(pl.Int64),
        pl.col("email").str.to_lowercase(),
        pl.col("age").cast(pl.Int32),
        pl.col("status").str.to_lowercase()
    ])
    print(transformed_data)
    
    # Validate transformation
    schema_validator = PolarsSchemaValidator({
        "user_id": pl.Int64,
        "email": pl.Utf8,
        "age": pl.Int32,
        "status": pl.Utf8
    })
    schema_result = schema_validator.validate(transformed_data)
    print(f"Transformation validation: {'✓ PASSED' if schema_result.passed else '✗ FAILED'}")
    
    # Stage 3: Load (validate before loading)
    print("\nStage 3: Load Validation")
    load_validator = PolarsValidator()
    load_validator.expect_column_not_null("user_id")
    load_validator.expect_column_unique("user_id")
    load_validator.expect_column_values_match_regex("email", r"^[\w\.-]+@[\w\.-]+\.\w+$")
    load_validator.expect_column_values_in_range("age", 0, 150)
    load_validator.expect_column_values_in_set("status", ["active", "inactive", "pending"])
    
    load_results = load_validator.validate(transformed_data)
    
    if load_validator.all_passed():
        print("✓ All validations passed - Ready to load!")
    else:
        print("✗ Validation failed - Fix issues before loading:")
        for result in load_validator.get_failed_validations():
            print(f"  - {result.message}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("POLARS-POWERED ETL TESTING FRAMEWORK")
    print("Comprehensive Examples")
    print("="*60)
    
    example_1_basic_validation()
    example_2_schema_validation()
    example_3_data_comparison()
    example_4_comprehensive_quality_check()
    example_5_lazy_evaluation_performance()
    example_6_etl_pipeline_testing()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
