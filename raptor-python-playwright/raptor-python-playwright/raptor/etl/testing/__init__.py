"""
RAPTOR ETL Testing Framework

Integration with open-source ETL testing frameworks for comprehensive
data pipeline testing, validation, and quality assurance.

Supported Frameworks:
- Great Expectations: Data validation and profiling
- Pandera: DataFrame schema validation
- Soda Core: SQL-based data quality checks
- dbt: Data transformation testing
- pytest-datatest: Data unit testing

Example Usage:
    from raptor.etl.testing import (
        GreatExpectationsValidator,
        PanderaValidator,
        SodaChecker,
        DataQualityTestSuite
    )
    
    # Great Expectations validation
    validator = GreatExpectationsValidator("user_data_suite")
    validator.expect_column_values_to_not_be_null("user_id")
    result = validator.validate(dataframe)
    
    # Pandera schema validation
    schema = pa.DataFrameSchema({...})
    pandera_validator = PanderaValidator(schema)
    validated_df = pandera_validator.validate(dataframe)
    
    # Soda quality checks
    checker = SodaChecker(data_source="postgresql")
    checker.add_check("row_count > 1000")
    results = checker.run_checks()
"""

from raptor.etl.testing.great_expectations_integration import (
    GreatExpectationsValidator,
    GreatExpectationsConfig,
    ExpectationSuite
)
from raptor.etl.testing.pandera_integration import (
    PanderaValidator,
    PanderaSchemaBuilder,
    DataFrameSchema
)
from raptor.etl.testing.soda_integration import (
    SodaChecker,
    SodaConfig,
    SodaCheck
)
from raptor.etl.testing.dbt_integration import (
    DBTTester,
    DBTConfig,
    DBTTest
)
from raptor.etl.testing.pytest_datatest_integration import (
    DataTestRunner,
    DataTestCase,
    DataAssertion
)
from raptor.etl.testing.test_suite import (
    DataQualityTestSuite,
    ETLTestRunner,
    TestResult,
    TestReport
)
from raptor.etl.testing.validators import (
    SchemaValidator,
    DataQualityValidator,
    TransformationValidator,
    LineageValidator
)
from raptor.etl.testing.comparators import (
    DataComparator,
    SchemaComparator,
    DiffResult
)
from raptor.etl.testing.reporters import (
    DataQualityDashboard,
    TestCoverageReporter,
    ValidationReporter
)
from raptor.etl.testing.models import (
    ValidationResult,
    TestStatus,
    QualityMetrics,
    CoverageReport
)

__all__ = [
    # Great Expectations
    'GreatExpectationsValidator',
    'GreatExpectationsConfig',
    'ExpectationSuite',
    
    # Pandera
    'PanderaValidator',
    'PanderaSchemaBuilder',
    'DataFrameSchema',
    
    # Soda Core
    'SodaChecker',
    'SodaConfig',
    'SodaCheck',
    
    # dbt
    'DBTTester',
    'DBTConfig',
    'DBTTest',
    
    # pytest-datatest
    'DataTestRunner',
    'DataTestCase',
    'DataAssertion',
    
    # Test Suite
    'DataQualityTestSuite',
    'ETLTestRunner',
    'TestResult',
    'TestReport',
    
    # Validators
    'SchemaValidator',
    'DataQualityValidator',
    'TransformationValidator',
    'LineageValidator',
    
    # Comparators
    'DataComparator',
    'SchemaComparator',
    'DiffResult',
    
    # Reporters
    'DataQualityDashboard',
    'TestCoverageReporter',
    'ValidationReporter',
    
    # Models
    'ValidationResult',
    'TestStatus',
    'QualityMetrics',
    'CoverageReport',
]

__version__ = '1.0.0'
