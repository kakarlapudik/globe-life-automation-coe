"""
Polars-based validators for ETL testing.

Provides high-performance data validation with type safety.
"""

import polars as pl
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    failed_rows: Optional[pl.DataFrame] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        status = "✓ PASSED" if self.passed else "✗ FAILED"
        return f"[{self.severity.value.upper()}] {status}: {self.check_name} - {self.message}"


class PolarsValidator:
    """
    High-performance validator for Polars DataFrames.
    
    Provides Great Expectations-style validations with Polars performance.
    
    Example:
        validator = PolarsValidator()
        validator.expect_column_not_null("user_id")
        validator.expect_column_unique("email")
        validator.expect_column_values_in_range("age", 0, 150)
        
        results = validator.validate(df)
        assert all(r.passed for r in results)
    """
    
    def __init__(self):
        self.expectations: List[Callable] = []
        self.results: List[ValidationResult] = []
    
    def expect_column_exists(
        self,
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column to exist in DataFrame."""
        def check(df: pl.DataFrame) -> ValidationResult:
            passed = column in df.columns
            return ValidationResult(
                check_name="expect_column_exists",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' {'exists' if passed else 'does not exist'}"
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_not_null(
        self,
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column to have no null values."""
        def check(df: pl.DataFrame) -> ValidationResult:
            null_count = df[column].null_count()
            passed = null_count == 0
            
            failed_rows = None
            if not passed:
                failed_rows = df.filter(pl.col(column).is_null())
            
            return ValidationResult(
                check_name="expect_column_not_null",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' has {null_count} null values",
                failed_rows=failed_rows,
                metadata={"null_count": null_count}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_unique(
        self,
        column: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column values to be unique."""
        def check(df: pl.DataFrame) -> ValidationResult:
            total_count = len(df)
            unique_count = df[column].n_unique()
            passed = total_count == unique_count
            
            failed_rows = None
            if not passed:
                # Find duplicate values
                duplicates = (
                    df
                    .group_by(column)
                    .agg(pl.count().alias("count"))
                    .filter(pl.col("count") > 1)
                )
                failed_rows = df.join(duplicates, on=column, how="inner")
            
            return ValidationResult(
                check_name="expect_column_unique",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' has {total_count - unique_count} duplicate values",
                failed_rows=failed_rows,
                metadata={"total_count": total_count, "unique_count": unique_count}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_values_in_range(
        self,
        column: str,
        min_value: Union[int, float],
        max_value: Union[int, float],
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column values to be within range."""
        def check(df: pl.DataFrame) -> ValidationResult:
            out_of_range = df.filter(
                (pl.col(column) < min_value) | (pl.col(column) > max_value)
            )
            passed = len(out_of_range) == 0
            
            return ValidationResult(
                check_name="expect_column_values_in_range",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' has {len(out_of_range)} values outside range [{min_value}, {max_value}]",
                failed_rows=out_of_range if not passed else None,
                metadata={"min_value": min_value, "max_value": max_value, "violations": len(out_of_range)}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_values_match_regex(
        self,
        column: str,
        pattern: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column values to match regex pattern."""
        def check(df: pl.DataFrame) -> ValidationResult:
            non_matching = df.filter(~pl.col(column).str.contains(pattern))
            passed = len(non_matching) == 0
            
            return ValidationResult(
                check_name="expect_column_values_match_regex",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' has {len(non_matching)} values not matching pattern '{pattern}'",
                failed_rows=non_matching if not passed else None,
                metadata={"pattern": pattern, "violations": len(non_matching)}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_values_in_set(
        self,
        column: str,
        value_set: List[Any],
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column values to be in specified set."""
        def check(df: pl.DataFrame) -> ValidationResult:
            invalid_values = df.filter(~pl.col(column).is_in(value_set))
            passed = len(invalid_values) == 0
            
            return ValidationResult(
                check_name="expect_column_values_in_set",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' has {len(invalid_values)} values not in allowed set",
                failed_rows=invalid_values if not passed else None,
                metadata={"allowed_values": value_set, "violations": len(invalid_values)}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_row_count_greater_than(
        self,
        threshold: int,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect DataFrame to have more than threshold rows."""
        def check(df: pl.DataFrame) -> ValidationResult:
            row_count = len(df)
            passed = row_count > threshold
            
            return ValidationResult(
                check_name="expect_row_count_greater_than",
                passed=passed,
                severity=severity,
                message=f"DataFrame has {row_count} rows (threshold: {threshold})",
                metadata={"row_count": row_count, "threshold": threshold}
            )
        
        self.expectations.append(check)
        return self
    
    def expect_column_mean_in_range(
        self,
        column: str,
        min_value: float,
        max_value: float,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        """Expect column mean to be within range."""
        def check(df: pl.DataFrame) -> ValidationResult:
            mean_value = df[column].mean()
            passed = min_value <= mean_value <= max_value
            
            return ValidationResult(
                check_name="expect_column_mean_in_range",
                passed=passed,
                severity=severity,
                message=f"Column '{column}' mean is {mean_value:.2f} (expected: [{min_value}, {max_value}])",
                metadata={"mean": mean_value, "min_value": min_value, "max_value": max_value}
            )
        
        self.expectations.append(check)
        return self
    
    def validate(self, df: pl.DataFrame) -> List[ValidationResult]:
        """
        Run all validations on DataFrame.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            List of validation results
        """
        self.results = []
        
        for expectation in self.expectations:
            try:
                result = expectation(df)
                self.results.append(result)
            except Exception as e:
                self.results.append(ValidationResult(
                    check_name="validation_error",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation failed with error: {str(e)}"
                ))
        
        return self.results
    
    def get_failed_validations(self) -> List[ValidationResult]:
        """Get only failed validations."""
        return [r for r in self.results if not r.passed]
    
    def all_passed(self) -> bool:
        """Check if all validations passed."""
        return all(r.passed for r in self.results)
    
    def generate_report(self) -> str:
        """Generate validation report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        report = f"\n{'='*60}\n"
        report += f"VALIDATION REPORT\n"
        report += f"{'='*60}\n"
        report += f"Total Checks: {total}\n"
        report += f"Passed: {passed} ({passed/total*100:.1f}%)\n"
        report += f"Failed: {failed} ({failed/total*100:.1f}%)\n"
        report += f"{'='*60}\n\n"
        
        for result in self.results:
            report += f"{result}\n"
        
        return report


class PolarsSchemaValidator:
    """
    Schema validator for Polars DataFrames.
    
    Provides type-safe schema validation with detailed error reporting.
    
    Example:
        schema = {
            "user_id": pl.Int64,
            "email": pl.Utf8,
            "age": pl.Int32,
            "created_at": pl.Datetime
        }
        
        validator = PolarsSchemaValidator(schema)
        result = validator.validate(df)
    """
    
    def __init__(self, schema: Dict[str, pl.DataType]):
        """
        Initialize schema validator.
        
        Args:
            schema: Dictionary mapping column names to Polars data types
        """
        self.schema = schema
    
    def validate(self, df: pl.DataFrame) -> ValidationResult:
        """
        Validate DataFrame against schema.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            ValidationResult
        """
        errors = []
        
        # Check for missing columns
        missing_columns = set(self.schema.keys()) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")
        
        # Check for extra columns
        extra_columns = set(df.columns) - set(self.schema.keys())
        if extra_columns:
            errors.append(f"Extra columns: {extra_columns}")
        
        # Check data types
        for column, expected_type in self.schema.items():
            if column in df.columns:
                actual_type = df[column].dtype
                if actual_type != expected_type:
                    errors.append(f"Column '{column}': expected {expected_type}, got {actual_type}")
        
        passed = len(errors) == 0
        message = "Schema validation passed" if passed else f"Schema validation failed: {'; '.join(errors)}"
        
        return ValidationResult(
            check_name="schema_validation",
            passed=passed,
            severity=ValidationSeverity.ERROR,
            message=message,
            metadata={"errors": errors}
        )
    
    def coerce_types(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Attempt to coerce DataFrame to match schema.
        
        Args:
            df: DataFrame to coerce
        
        Returns:
            DataFrame with coerced types
        """
        for column, dtype in self.schema.items():
            if column in df.columns:
                try:
                    df = df.with_columns(pl.col(column).cast(dtype))
                except Exception as e:
                    raise ValueError(f"Cannot coerce column '{column}' to {dtype}: {e}")
        
        return df


class PolarsDataQualityValidator:
    """
    Comprehensive data quality validator.
    
    Combines multiple validation strategies for thorough data quality checks.
    """
    
    def __init__(self):
        self.validators: List[PolarsValidator] = []
        self.schema_validator: Optional[PolarsSchemaValidator] = None
    
    def add_validator(self, validator: PolarsValidator):
        """Add a validator to the quality check suite."""
        self.validators.append(validator)
        return self
    
    def set_schema(self, schema: Dict[str, pl.DataType]):
        """Set schema for validation."""
        self.schema_validator = PolarsSchemaValidator(schema)
        return self
    
    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """
        Run comprehensive data quality validation.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Dictionary with validation results and quality metrics
        """
        all_results = []
        
        # Schema validation
        if self.schema_validator:
            schema_result = self.schema_validator.validate(df)
            all_results.append(schema_result)
        
        # Run all validators
        for validator in self.validators:
            results = validator.validate(df)
            all_results.extend(results)
        
        # Calculate quality score
        total_checks = len(all_results)
        passed_checks = sum(1 for r in all_results if r.passed)
        quality_score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        return {
            "results": all_results,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "quality_score": quality_score,
            "all_passed": all(r.passed for r in all_results)
        }
