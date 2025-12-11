"""
High-performance data comparison utilities using Polars.

Provides fast data diff and comparison operations.
"""

import polars as pl
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class DiffType(Enum):
    """Types of differences between datasets."""
    ADDED = "added"  # Rows in target but not in source
    REMOVED = "removed"  # Rows in source but not in target
    MODIFIED = "modified"  # Rows with different values
    UNCHANGED = "unchanged"  # Rows that are identical


@dataclass
class DiffResult:
    """Result of data comparison."""
    added_rows: pl.DataFrame
    removed_rows: pl.DataFrame
    modified_rows: pl.DataFrame
    unchanged_count: int
    total_source_rows: int
    total_target_rows: int
    key_columns: List[str]
    compare_columns: List[str]
    
    @property
    def has_differences(self) -> bool:
        """Check if there are any differences."""
        return (
            len(self.added_rows) > 0 or
            len(self.removed_rows) > 0 or
            len(self.modified_rows) > 0
        )
    
    @property
    def match_percentage(self) -> float:
        """Calculate percentage of matching rows."""
        total = max(self.total_source_rows, self.total_target_rows)
        if total == 0:
            return 100.0
        return (self.unchanged_count / total) * 100
    
    def summary(self) -> str:
        """Generate summary of differences."""
        summary = f"\n{'='*60}\n"
        summary += f"DATA COMPARISON SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Source Rows: {self.total_source_rows}\n"
        summary += f"Target Rows: {self.total_target_rows}\n"
        summary += f"Unchanged: {self.unchanged_count}\n"
        summary += f"Added: {len(self.added_rows)}\n"
        summary += f"Removed: {len(self.removed_rows)}\n"
        summary += f"Modified: {len(self.modified_rows)}\n"
        summary += f"Match Percentage: {self.match_percentage:.2f}%\n"
        summary += f"{'='*60}\n"
        return summary


class PolarsDataComparator:
    """
    High-performance data comparator using Polars.
    
    Provides fast comparison of large datasets with detailed diff reporting.
    
    Example:
        comparator = PolarsDataComparator()
        diff = comparator.compare(
            source_df=staging_data,
            target_df=production_data,
            key_columns=["user_id"],
            compare_columns=["email", "name", "status"]
        )
        
        print(diff.summary())
        if diff.has_differences:
            print(f"Added rows: {len(diff.added_rows)}")
            print(f"Modified rows: {len(diff.modified_rows)}")
    """
    
    def compare(
        self,
        source_df: pl.DataFrame,
        target_df: pl.DataFrame,
        key_columns: List[str],
        compare_columns: Optional[List[str]] = None,
        ignore_columns: Optional[List[str]] = None
    ) -> DiffResult:
        """
        Compare two DataFrames and identify differences.
        
        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            key_columns: Columns to use as unique identifiers
            compare_columns: Columns to compare (None = all columns except keys)
            ignore_columns: Columns to ignore in comparison
        
        Returns:
            DiffResult with detailed comparison
        """
        # Determine columns to compare
        if compare_columns is None:
            compare_columns = [c for c in source_df.columns if c not in key_columns]
        
        if ignore_columns:
            compare_columns = [c for c in compare_columns if c not in ignore_columns]
        
        # Find added rows (in target but not in source)
        added_rows = target_df.join(
            source_df.select(key_columns),
            on=key_columns,
            how="anti"
        )
        
        # Find removed rows (in source but not in target)
        removed_rows = source_df.join(
            target_df.select(key_columns),
            on=key_columns,
            how="anti"
        )
        
        # Find rows that exist in both (for modification check)
        common_keys = source_df.join(
            target_df.select(key_columns),
            on=key_columns,
            how="inner"
        ).select(key_columns)
        
        # Get full rows for common keys from both datasets
        source_common = source_df.join(common_keys, on=key_columns, how="inner")
        target_common = target_df.join(common_keys, on=key_columns, how="inner")
        
        # Find modified rows by comparing values
        modified_rows = self._find_modified_rows(
            source_common,
            target_common,
            key_columns,
            compare_columns
        )
        
        # Calculate unchanged count
        unchanged_count = len(common_keys) - len(modified_rows)
        
        return DiffResult(
            added_rows=added_rows,
            removed_rows=removed_rows,
            modified_rows=modified_rows,
            unchanged_count=unchanged_count,
            total_source_rows=len(source_df),
            total_target_rows=len(target_df),
            key_columns=key_columns,
            compare_columns=compare_columns
        )
    
    def _find_modified_rows(
        self,
        source_df: pl.DataFrame,
        target_df: pl.DataFrame,
        key_columns: List[str],
        compare_columns: List[str]
    ) -> pl.DataFrame:
        """
        Find rows with modified values.
        
        Args:
            source_df: Source DataFrame (common keys only)
            target_df: Target DataFrame (common keys only)
            key_columns: Key columns
            compare_columns: Columns to compare
        
        Returns:
            DataFrame with modified rows and change details
        """
        # Join source and target with suffixes
        joined = source_df.join(
            target_df,
            on=key_columns,
            how="inner",
            suffix="_target"
        )
        
        # Build condition to find rows with any differences
        conditions = []
        for col in compare_columns:
            source_col = col
            target_col = f"{col}_target"
            
            if target_col in joined.columns:
                # Handle nulls properly in comparison
                conditions.append(
                    (pl.col(source_col) != pl.col(target_col)) |
                    (pl.col(source_col).is_null() != pl.col(target_col).is_null())
                )
        
        if not conditions:
            return pl.DataFrame()
        
        # Combine all conditions with OR
        combined_condition = conditions[0]
        for condition in conditions[1:]:
            combined_condition = combined_condition | condition
        
        # Filter to rows with differences
        modified = joined.filter(combined_condition)
        
        return modified
    
    def compare_schemas(
        self,
        source_df: pl.DataFrame,
        target_df: pl.DataFrame
    ) -> Dict[str, Any]:
        """
        Compare schemas of two DataFrames.
        
        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
        
        Returns:
            Dictionary with schema comparison results
        """
        source_schema = {col: dtype for col, dtype in zip(source_df.columns, source_df.dtypes)}
        target_schema = {col: dtype for col, dtype in zip(target_df.columns, target_df.dtypes)}
        
        source_cols = set(source_schema.keys())
        target_cols = set(target_schema.keys())
        
        added_columns = target_cols - source_cols
        removed_columns = source_cols - target_cols
        common_columns = source_cols & target_cols
        
        type_changes = {}
        for col in common_columns:
            if source_schema[col] != target_schema[col]:
                type_changes[col] = {
                    "source_type": source_schema[col],
                    "target_type": target_schema[col]
                }
        
        return {
            "schemas_match": (
                len(added_columns) == 0 and
                len(removed_columns) == 0 and
                len(type_changes) == 0
            ),
            "added_columns": list(added_columns),
            "removed_columns": list(removed_columns),
            "type_changes": type_changes,
            "source_schema": source_schema,
            "target_schema": target_schema
        }


class PolarsSchemaComparator:
    """
    Schema comparator for detecting schema evolution and breaking changes.
    """
    
    def compare(
        self,
        old_schema: Dict[str, pl.DataType],
        new_schema: Dict[str, pl.DataType]
    ) -> Dict[str, Any]:
        """
        Compare two schemas and identify changes.
        
        Args:
            old_schema: Old schema definition
            new_schema: New schema definition
        
        Returns:
            Dictionary with schema comparison results
        """
        old_cols = set(old_schema.keys())
        new_cols = set(new_schema.keys())
        
        added_columns = new_cols - old_cols
        removed_columns = old_cols - new_cols
        common_columns = old_cols & new_cols
        
        type_changes = {}
        for col in common_columns:
            if old_schema[col] != new_schema[col]:
                type_changes[col] = {
                    "old_type": old_schema[col],
                    "new_type": new_schema[col],
                    "is_compatible": self._is_type_compatible(old_schema[col], new_schema[col])
                }
        
        # Determine if changes are backward compatible
        breaking_changes = []
        
        if removed_columns:
            breaking_changes.append(f"Removed columns: {removed_columns}")
        
        for col, change in type_changes.items():
            if not change["is_compatible"]:
                breaking_changes.append(
                    f"Incompatible type change for '{col}': {change['old_type']} -> {change['new_type']}"
                )
        
        is_backward_compatible = len(breaking_changes) == 0
        
        return {
            "is_backward_compatible": is_backward_compatible,
            "breaking_changes": breaking_changes,
            "added_columns": list(added_columns),
            "removed_columns": list(removed_columns),
            "type_changes": type_changes
        }
    
    def _is_type_compatible(
        self,
        old_type: pl.DataType,
        new_type: pl.DataType
    ) -> bool:
        """
        Check if type change is compatible.
        
        Args:
            old_type: Old data type
            new_type: New data type
        
        Returns:
            True if compatible, False otherwise
        """
        # Same type is always compatible
        if old_type == new_type:
            return True
        
        # Define compatible type transitions
        compatible_transitions = {
            pl.Int32: [pl.Int64, pl.Float32, pl.Float64],
            pl.Int64: [pl.Float64],
            pl.Float32: [pl.Float64],
            pl.Utf8: [],  # String changes are usually breaking
        }
        
        return new_type in compatible_transitions.get(old_type, [])


class PolarsDiffEngine:
    """
    Advanced diff engine for complex data comparisons.
    
    Provides detailed change tracking and reconciliation capabilities.
    """
    
    def __init__(self):
        self.comparator = PolarsDataComparator()
    
    def generate_reconciliation_report(
        self,
        source_df: pl.DataFrame,
        target_df: pl.DataFrame,
        key_columns: List[str],
        compare_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive reconciliation report.
        
        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            key_columns: Key columns
            compare_columns: Columns to compare
        
        Returns:
            Detailed reconciliation report
        """
        diff = self.comparator.compare(
            source_df,
            target_df,
            key_columns,
            compare_columns
        )
        
        schema_comparison = self.comparator.compare_schemas(source_df, target_df)
        
        return {
            "data_diff": diff,
            "schema_comparison": schema_comparison,
            "summary": diff.summary(),
            "requires_action": diff.has_differences or not schema_comparison["schemas_match"]
        }
    
    def export_diff_to_excel(
        self,
        diff: DiffResult,
        output_path: str
    ):
        """
        Export diff results to Excel file.
        
        Args:
            diff: DiffResult to export
            output_path: Path to output Excel file
        """
        # This would use a library like openpyxl or xlsxwriter
        # For now, we'll export to CSV files
        if len(diff.added_rows) > 0:
            diff.added_rows.write_csv(output_path.replace(".xlsx", "_added.csv"))
        
        if len(diff.removed_rows) > 0:
            diff.removed_rows.write_csv(output_path.replace(".xlsx", "_removed.csv"))
        
        if len(diff.modified_rows) > 0:
            diff.modified_rows.write_csv(output_path.replace(".xlsx", "_modified.csv"))
