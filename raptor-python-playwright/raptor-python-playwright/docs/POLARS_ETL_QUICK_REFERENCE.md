# Polars ETL Testing - Quick Reference

## Installation

```bash
pip install raptor-playwright[etl]
pip install polars>=0.20.0
```

## Basic Validation

```python
import polars as pl
from raptor.etl import PolarsValidator

df = pl.read_csv("data.csv")

validator = PolarsValidator()
validator.expect_column_not_null("id")
validator.expect_column_unique("email")
validator.expect_column_values_in_range("age", 0, 150)

results = validator.validate(df)
print(validator.generate_report())
```

## Schema Validation

```python
from raptor.etl import PolarsSchemaValidator

schema = {
    "user_id": pl.Int64,
    "email": pl.Utf8,
    "age": pl.Int32
}

validator = PolarsSchemaValidator(schema)
result = validator.validate(df)

if not result.passed:
    df = validator.coerce_types(df)
```

## Data Comparison

```python
from raptor.etl import PolarsDataComparator

comparator = PolarsDataComparator()
diff = comparator.compare(
    source_df=staging_df,
    target_df=prod_df,
    key_columns=["id"],
    compare_columns=["email", "name"]
)

print(diff.summary())
```

## Lazy Evaluation

```python
from raptor.etl import PolarsEngine

engine = PolarsEngine()
df = engine.read_csv("large_file.csv", lazy=True)
df = engine.filter(df, pl.col("year") == 2024)
result = engine.collect(df)
```

## Streaming

```python
from raptor.etl import PolarsStreamingEngine

engine = PolarsStreamingEngine()
df = pl.scan_csv("huge_file.csv")
result = engine.collect_streaming(df)
```

## Common Validations

| Validation | Code |
|------------|------|
| Not Null | `validator.expect_column_not_null("col")` |
| Unique | `validator.expect_column_unique("col")` |
| Range | `validator.expect_column_values_in_range("col", 0, 100)` |
| Regex | `validator.expect_column_values_match_regex("col", r"pattern")` |
| Value Set | `validator.expect_column_values_in_set("col", ["A", "B"])` |
| Row Count | `validator.expect_row_count_greater_than(1000)` |

## Performance Tips

1. **Use Lazy Loading**
   ```python
   df = pl.scan_csv("file.csv")  # Not pl.read_csv()
   ```

2. **Use Streaming for Large Data**
   ```python
   result = df.collect(streaming=True)
   ```

3. **Use Expressions**
   ```python
   df = df.with_columns((pl.col("a") + pl.col("b")).alias("c"))
   ```

4. **Avoid Loops**
   ```python
   # Bad: for i in range(len(df))
   # Good: df.with_columns(...)
   ```

## Pandas to Polars

| Pandas | Polars |
|--------|--------|
| `df[df['col'] > 5]` | `df.filter(pl.col('col') > 5)` |
| `df['new'] = df['old'] * 2` | `df.with_columns((pl.col('old') * 2).alias('new'))` |
| `df.groupby('col').agg({'val': 'sum'})` | `df.group_by('col').agg(pl.col('val').sum())` |
| `df.merge(df2, on='id')` | `df.join(df2, on='id')` |

## Resources

- [Complete Guide](../POLARS_ETL_TESTING_GUIDE.md)
- [Migration Guide](../PANDAS_TO_POLARS_MIGRATION.md)
- [Examples](../examples/polars_etl_example.py)
- [API Reference](API_REFERENCE_GUIDE.md)
