# RAPTOR Python Playwright Framework
## Certification Quiz

---

## Instructions

- **Total Questions**: 20
- **Passing Score**: 80% (16 correct answers)
- **Time Limit**: 30 minutes
- **Format**: Multiple choice (single answer)
- **Open Book**: You may reference documentation

### How to Take the Quiz
1. Read each question carefully
2. Select the best answer
3. Mark your answers on paper or in a separate file
4. Check your answers at the end
5. Score 16+ correct to pass and receive certification

---

## Questions

### Question 1
What does RAPTOR stand for?

A) Rapid Automated Python Test Orchestration & Reporting  
B) Robust Automated Playwright Test Orchestration & Reporting  
C) Reliable Automated Python Testing & Optimization Runtime  
D) Robust Automated Python Test Organization & Reporting

---

### Question 2
Which browsers does RAPTOR support through Playwright?

A) Chrome and Firefox only  
B) Chromium, Firefox, and Safari  
C) Chromium, Firefox, and WebKit  
D) All major browsers including IE11

---

### Question 3
What is the correct way to mark an async test function in pytest?

A) `@pytest.async`  
B) `@pytest.mark.asyncio`  
C) `@async_test`  
D) `def async test_name():`

---

### Question 4
Which locator strategy is NOT supported by RAPTOR?

A) CSS Selector  
B) XPath  
C) Text content  
D) Java Reflection

---

### Question 5
What happens when a primary locator fails in ElementManager?

A) The test immediately fails  
B) It retries the same locator 3 times  
C) It automatically tries fallback locators  
D) It waits 30 seconds then fails

---

### Question 6
How do you fill a text field using ElementManager?

A) `element_manager.fill("locator", "text")`  
B) `element_manager.type("locator", "text")`  
C) `element_manager.send_keys("locator", "text")`  
D) `element_manager.input("locator", "text")`

---

### Question 7
What is the main benefit of session reuse in RAPTOR?

A) Better security  
B) Reduced test startup time  
C) Improved test accuracy  
D) Automatic error recovery

---

### Question 8
Which command saves a browser session?

A) `session_manager.save(page, "name")`  
B) `session_manager.store_session(page, "name")`  
C) `session_manager.save_session(page, "name")`  
D) `session_manager.persist(page, "name")`

---

### Question 9
What is the purpose of the Page Object Model pattern?

A) To make tests run faster  
B) To create maintainable and reusable test code  
C) To reduce memory usage  
D) To enable parallel execution

---

### Question 10
Which class should all page objects inherit from?

A) `PageObject`  
B) `BasePage`  
C) `RaptorPage`  
D) `AbstractPage`

---

### Question 11
How do you run tests in parallel using pytest?

A) `pytest --parallel`  
B) `pytest -n 4`  
C) `pytest --workers=4`  
D) `pytest --concurrent`

---

### Question 12
What does the `@pytest.mark.parametrize` decorator do?

A) Marks tests as parameterized for reporting  
B) Runs the same test with different data sets  
C) Enables parallel execution  
D) Adds parameters to test fixtures

---

### Question 13
Which method is used to verify an element exists?

A) `element_manager.check_exists("locator")`  
B) `element_manager.verify_exists("locator")`  
C) `element_manager.assert_exists("locator")`  
D) `element_manager.is_present("locator")`

---

### Question 14
What is the difference between hard and soft assertions?

A) Hard assertions are faster  
B) Soft assertions continue execution after failure  
C) Hard assertions are more accurate  
D) Soft assertions don't generate reports

---

### Question 15
How do you find a table row by key value using TableManager?

A) `table_manager.find_row("table", "key")`  
B) `table_manager.locate_row_by_key("table", column, "key")`  
C) `table_manager.find_row_by_key("table", column, "key")`  
D) `table_manager.search_row("table", column, "key")`

---

### Question 16
Which database systems does RAPTOR support for DDDB integration?

A) MySQL and PostgreSQL  
B) SQL Server and Access  
C) MongoDB and Redis  
D) Oracle and DB2

---

### Question 17
What is the correct way to load environment-specific configuration?

A) `config.load("dev")`  
B) `config.load_config(environment="dev")`  
C) `config.set_environment("dev")`  
D) `config.use("dev")`

---

### Question 18
How do you take a screenshot in RAPTOR?

A) `page.screenshot(path="file.png")`  
B) `element_manager.capture("file.png")`  
C) `browser.screenshot("file.png")`  
D) `raptor.screenshot("file.png")`

---

### Question 19
What is the default timeout for element operations in RAPTOR?

A) 10 seconds  
B) 15 seconds  
C) 20 seconds  
D) 30 seconds

---

### Question 20
Which CLI command lists all saved sessions?

A) `raptor sessions`  
B) `raptor session list`  
C) `raptor list-sessions`  
D) `raptor show sessions`

---

## Answer Key

<details>
<summary>Click to reveal answers (only after completing the quiz!)</summary>

### Answers

1. **B** - Robust Automated Playwright Test Orchestration & Reporting
2. **C** - Chromium, Firefox, and WebKit
3. **B** - `@pytest.mark.asyncio`
4. **D** - Java Reflection
5. **C** - It automatically tries fallback locators
6. **A** - `element_manager.fill("locator", "text")`
7. **B** - Reduced test startup time
8. **C** - `session_manager.save_session(page, "name")`
9. **B** - To create maintainable and reusable test code
10. **B** - `BasePage`
11. **B** - `pytest -n 4`
12. **B** - Runs the same test with different data sets
13. **B** - `element_manager.verify_exists("locator")`
14. **B** - Soft assertions continue execution after failure
15. **C** - `table_manager.find_row_by_key("table", column, "key")`
16. **B** - SQL Server and Access
17. **B** - `config.load_config(environment="dev")`
18. **A** - `page.screenshot(path="file.png")`
19. **C** - 20 seconds
20. **B** - `raptor session list`

### Scoring

- **20 correct**: Perfect score! 🏆
- **18-19 correct**: Excellent! 🌟
- **16-17 correct**: Pass! ✅
- **14-15 correct**: Close! Review and retake
- **Below 14**: Study more and retake

</details>

---

## Detailed Explanations

<details>
<summary>Click for detailed explanations of each answer</summary>

### Question 1 Explanation
RAPTOR stands for **Robust Automated Playwright Test Orchestration & Reporting**. The framework emphasizes robustness through fallback strategies, Playwright as the core automation engine, and comprehensive reporting capabilities.

### Question 2 Explanation
Playwright supports **Chromium, Firefox, and WebKit**. Note that WebKit is the browser engine used by Safari, not Safari itself. This gives excellent cross-browser coverage for modern web applications.

### Question 3 Explanation
The correct decorator is `@pytest.mark.asyncio`. This tells pytest that the test function is asynchronous and should be run with an event loop. It's required for all async test functions.

### Question 4 Explanation
**Java Reflection** is not a locator strategy. RAPTOR supports CSS selectors, XPath, text content, role-based (accessibility), and ID-based locators.

### Question 5 Explanation
When a primary locator fails, ElementManager **automatically tries fallback locators** in the order they were provided. This makes tests more resilient to UI changes.

### Question 6 Explanation
The correct method is `element_manager.fill("locator", "text")`. This is Playwright's terminology, which differs from Selenium's `send_keys()`.

### Question 7 Explanation
The main benefit is **reduced test startup time**. By saving a session after login or setup, you can restore it in subsequent test runs, skipping expensive setup steps. This can reduce startup time by 50% or more.

### Question 8 Explanation
The correct method is `session_manager.save_session(page, "name")`. This saves the current browser state including cookies, local storage, and session storage.

### Question 9 Explanation
The Page Object Model pattern helps **create maintainable and reusable test code** by encapsulating page-specific logic and locators in dedicated classes, separating test logic from page structure.

### Question 10 Explanation
All page objects should inherit from **BasePage**, which provides common functionality like navigation, screenshot capture, and script execution.

### Question 11 Explanation
The correct command is `pytest -n 4`, which runs tests in parallel using 4 workers. This requires the pytest-xdist plugin.

### Question 12 Explanation
`@pytest.mark.parametrize` **runs the same test with different data sets**. This is essential for data-driven testing, allowing you to test multiple scenarios with a single test function.

### Question 13 Explanation
The correct method is `element_manager.verify_exists("locator")`. This performs a hard assertion that will fail the test if the element doesn't exist.

### Question 14 Explanation
**Soft assertions continue execution after failure**, collecting all failures and reporting them at the end. Hard assertions stop execution immediately on failure.

### Question 15 Explanation
The correct method is `table_manager.find_row_by_key("table", column, "key")`. This searches for a row where the specified column contains the key value.

### Question 16 Explanation
RAPTOR supports **SQL Server and Access** for DDDB integration, maintaining compatibility with the existing Java framework's database infrastructure.

### Question 17 Explanation
The correct method is `config.load_config(environment="dev")`. This loads the configuration file for the specified environment (dev, staging, prod).

### Question 18 Explanation
The correct method is `page.screenshot(path="file.png")`. This is a Playwright Page method that captures a screenshot of the current page.

### Question 19 Explanation
The default timeout is **20 seconds** (20000 milliseconds). This can be configured globally or per-operation.

### Question 20 Explanation
The correct command is `raptor session list`. This CLI command displays all saved sessions with their metadata.

</details>

---

## Certification

### If You Passed (16+ correct)

**Congratulations! 🎉**

You have successfully completed the RAPTOR Python Playwright Framework certification.

#### Your Certificate

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              CERTIFICATE OF COMPLETION                   ║
║                                                          ║
║                  RAPTOR Framework                        ║
║         Python Playwright Test Automation                ║
║                                                          ║
║                  This certifies that                     ║
║                                                          ║
║                   [YOUR NAME]                            ║
║                                                          ║
║         has successfully completed the training          ║
║         and demonstrated proficiency in the              ║
║         RAPTOR Python Playwright Framework               ║
║                                                          ║
║              Score: [YOUR SCORE]/20                      ║
║              Date: [TODAY'S DATE]                        ║
║                                                          ║
║         ___________________________________________      ║
║         Test Automation Team Lead                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

#### Next Steps
1. ✅ Add certification to your profile
2. ✅ Start converting tests to RAPTOR
3. ✅ Join the RAPTOR community
4. ✅ Help train other team members

### If You Didn't Pass (Below 16 correct)

**Don't worry!** Learning takes time.

#### Recommended Actions
1. 📚 Review the training presentation
2. 💻 Complete the hands-on exercises again
3. 📖 Read the documentation sections you struggled with
4. 🔄 Retake the quiz when ready

#### Study Resources
- **Training Presentation**: `TRAINING_PRESENTATION.md`
- **Hands-On Exercises**: `HANDS_ON_EXERCISES.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **API Reference**: `docs/API_REFERENCE_GUIDE.md`
- **Examples**: `examples/`

---

## Feedback

### Help Us Improve

Please provide feedback on the training:

1. **What was most helpful?**
2. **What was most challenging?**
3. **What topics need more coverage?**
4. **How can we improve the exercises?**
5. **Overall rating (1-5 stars)?**

Send feedback to: test-automation-team@company.com

---

## Additional Resources

### Advanced Topics
After certification, explore these advanced topics:
- Property-based testing with Hypothesis
- CI/CD integration
- Performance testing
- Visual regression testing
- Custom reporters and integrations

### Community
- 💬 Slack: #raptor-framework
- 📧 Email: test-automation-team@company.com
- 🐛 Issues: GitHub Issues
- 📚 Wiki: Internal documentation

**Thank you for completing the RAPTOR certification! 🚀**
