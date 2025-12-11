# eServiceCenter V2 Repository Analysis

## Repository Overview

**Repository URL:** https://devops.globelifeinc.com/projects/Test%20Automation/_git/eServiceCenter_V2

**Purpose:** Java-based test automation framework for eService Center V2.0 application using Selenium WebDriver and TestNG

**Technology Stack:**
- Java 22 (compiled to Java 11)
- Maven 3.x
- TestNG 7.7.0
- Selenium WebDriver 4.11.0
- Appium 8.6.0 (Mobile testing)
- ExtentReports 5.1.1 (Reporting)
- Rest Assured 5.3.0 (API testing)

## Repository Structure

```
eServiceCenter_V2/
├── src/
│   └── test/
│       └── java/
│           └── globe/
│               └── life/
│                   ├── base/              # Base test classes
│                   ├── configreader/      # Configuration management
│                   ├── emailtemplates/    # Email templates
│                   ├── examples/          # Example tests
│                   ├── listeners/         # TestNG listeners
│                   ├── pages/             # Page Object Model classes
│                   ├── properties/        # Property files
│                   ├── screens/           # Mobile screen objects
│                   ├── secretserver/      # AWS Secrets Manager integration
│                   ├── testdata/          # Test data management
│                   ├── tests/             # Test classes
│                   ├── utils/             # Utility classes
│                   └── workspace/         # Workspace utilities
├── Jars/                                  # External JAR dependencies
├── out/                                   # Build output
├── pom.xml                                # Maven configuration
├── Smoke.xml                              # Smoke test suite
├── Regression.xml                         # Regression test suite
├── RegressionAPI.xml                      # API regression suite
├── RegressionUI.xml                       # UI regression suite
├── azure-pipelines.yml                    # Azure DevOps pipeline
├── azure-pipelines1.yml                   # Alternative pipeline
└── Selenium_CI.yml                        # CI pipeline configuration
```

## Test Suite Configuration

### Smoke Test Suite (Smoke.xml)

```xml
<suite name="eService V2" parallel="methods" thread-count="1">
    <listeners>
        <listener class-name="globe.life.listeners.EmailReportSuiteListener"/>
    </listeners>
    <parameter name="ReportName" value="eServiceV2_smokeTestReport.html"/>
    <test name="Smoke Test">
        <classes>
            <class name="globe.life.tests.SmokeTest"/>
        </classes>
    </test>
</suite>
```

**Key Features:**
- Parallel execution at method level
- Email report listener integration
- Configurable report naming
- Single smoke test class execution

### Test Scenarios Covered

The `SmokeTest` class covers:
1. Launch eService Center V2.0
2. Login functionality
3. Dashboard navigation
4. Bank Draft payment processing
5. Bank Draft payment validation
6. Credit Card payment processing
7. Credit Card payment validation
8. Registration page validation
9. Pay Your Bill page validation
10. Forgot Email functionality
11. Forgot Password functionality

## Maven Configuration

### Build Profiles

1. **Smoke Profile**
   - Executes: `Smoke.xml`
   - Command: `mvn test -P Smoke`

2. **Regression Profile**
   - Executes: `Regression.xml`
   - Command: `mvn test -P Regression`

### Key Dependencies

**Testing Frameworks:**
- TestNG 7.7.0
- Selenium Java 4.11.0
- Appium Java Client 8.6.0
- Rest Assured 5.3.0

**Reporting:**
- ExtentReports 5.1.1
- Test Data Supplier 1.9.7

**Database Connectivity:**
- PostgreSQL 42.2.18
- MySQL Connector 8.0.31
- MS SQL Server 8.4.1

**Cloud Integration:**
- AWS Secrets Manager SDK 2.18.41

**Utilities:**
- Apache POI 5.2.2 (Excel handling)
- Apache PDFBox 2.0.27 (PDF handling)
- Mailosaur 7.12.0 (Email testing)
- JavaFaker 1.0.2 (Test data generation)

## Test Execution Flow

### Data-Driven Testing

The framework uses MySQL database for test data management:

```java
@DataSupplier(runInParallel = false)
public synchronized String[] getPolicyAndIterationsFromDB() {
    String testCaseName = "SmokeTest";
    loadeSecV2Data(testCaseName);
    String[] pkidRowsForCurrIteration = getColVals(
        "select PKID from ES_All_TestData where Tester= '" + 
        ConfigFile.tester + "' and TestCase = '"+testCaseName+"' order by PKID asc;"
    );
    DataSource.closeMySQL();
    return pkidRowsForCurrIteration;
}
```

### Cross-Browser/Cross-Platform Testing

The framework supports:
- **Web Browsers:** Chrome, Firefox, Edge, Safari
- **Mobile Platforms:** iOS and Android via Appium
- **Cloud Testing:** LambdaTest integration for cross-browser testing

Test configuration includes:
- `LT_TestType`: web or mobile
- `LT_Browser`: Browser name
- `LT_BrowserOS`: Operating system
- `LT_BrowserVersion`: Browser version
- `LT_MobileDeviceName`: Mobile device name
- `LT_MobileDeviceOSVersion`: Mobile OS version

## Integration Points

### AWS Integration
- AWS Secrets Manager for credential management
- Secure storage of sensitive test data

### Email Testing
- Mailosaur integration for email validation
- Email report generation via custom listeners

### Database Integration
- MySQL for test data storage
- PostgreSQL support
- MS SQL Server support

### CI/CD Integration
- Azure DevOps pipelines
- Multiple pipeline configurations for different test suites

## Framework Architecture

### Page Object Model (POM)
- Separate page classes in `globe.life.pages` package
- Screen objects for mobile testing in `globe.life.screens`
- Reusable page components

### Base Test Classes
- `ProjectBaseTesteServiceCenter` - Base class for all tests
- Driver management and initialization
- Test step tracking and reporting

### Listeners
- `EmailReportSuiteListener` - Email report generation
- Custom TestNG listeners for enhanced reporting

### Configuration Management
- `ConfigFile` - Configuration reader
- Property-based configuration
- Environment-specific settings

### Test Data Management
- `DataSource` - Database connectivity and data retrieval
- Excel-based test data support
- Dynamic test data generation using JavaFaker

## Current Deployment Process

Based on the repository structure, the current process likely involves:

1. **Code Commit** → Azure DevOps repository
2. **Pipeline Trigger** → Azure Pipelines (azure-pipelines.yml)
3. **Build** → Maven compilation
4. **Test Execution** → TestNG suite execution
5. **Reporting** → ExtentReports generation
6. **Notification** → Email reports via listeners

## Framework Migration Considerations

### For Pipeline Design Framework Integration

**Strengths:**
- Well-structured Maven project
- Multiple test suite configurations
- Comprehensive dependency management
- Cloud testing integration (LambdaTest)
- Database-driven test data

**Challenges:**
- Custom JAR dependency (`Project 6.5.jar`) in local Jars folder
- Database dependency for test data
- Email notification configuration
- AWS Secrets Manager integration
- Multiple pipeline configurations to consolidate

**Migration Requirements:**
1. Maintain Maven build structure
2. Preserve TestNG suite configurations
3. Ensure database connectivity in CI/CD
4. Configure AWS credentials for Secrets Manager
5. Set up email notification service
6. Handle custom JAR dependencies
7. Configure LambdaTest credentials for cross-browser testing

## Recommendations for Framework Adoption

### Phase 1: Assessment
- ✅ Repository structure analyzed
- ✅ Dependencies documented
- ✅ Test execution flow understood
- ⏳ Current pipeline configuration review needed

### Phase 2: Framework Integration
- Create eServiceCenter-specific azure-pipelines.yml using framework templates
- Configure Maven build in Azure Pipelines
- Set up AWS service connection for Secrets Manager
- Configure database connection strings in variable groups
- Set up LambdaTest credentials

### Phase 3: Testing & Validation
- Execute smoke tests using new pipeline
- Validate reporting functionality
- Verify email notifications
- Test cross-browser execution

### Phase 4: Documentation
- Create eServiceCenter-specific setup guide
- Document variable group configuration
- Create troubleshooting guide
- Provide team training materials

## Next Steps

1. Review existing Azure Pipeline configurations (azure-pipelines.yml, azure-pipelines1.yml, Selenium_CI.yml)
2. Identify variable groups and service connections currently in use
3. Map current deployment workflow to framework patterns
4. Create migration plan with minimal disruption
5. Set up test environment for pilot deployment
