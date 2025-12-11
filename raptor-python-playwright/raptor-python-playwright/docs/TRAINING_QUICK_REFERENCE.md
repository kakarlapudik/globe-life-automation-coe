# RAPTOR Training - Quick Reference Guide

## 📚 Training Materials at a Glance

### Complete Training Package
All materials located in: `training/`

---

## 🎯 Quick Start

### For New Learners
1. Read `training/README.md` (10 min)
2. Review `training/TRAINING_PRESENTATION.md` (60 min)
3. Complete `training/HANDS_ON_EXERCISES.md` (3-4 hours)
4. Take `training/CERTIFICATION_QUIZ.md` (30 min)

### For Experienced Selenium Users
1. Skim presentation, focus on differences (30 min)
2. Complete all exercises (3 hours)
3. Take certification quiz (30 min)
4. Start converting tests

---

## 📖 Material Descriptions

### 1. Training Presentation
- **File**: `training/TRAINING_PRESENTATION.md`
- **Duration**: 60 minutes
- **Content**: 24 slides covering framework overview, components, usage
- **Best for**: Initial learning, group sessions

### 2. Hands-On Exercises
- **File**: `training/HANDS_ON_EXERCISES.md`
- **Duration**: 3-4 hours
- **Content**: 4 progressive exercises + bonus
- **Best for**: Practical skill building

### 3. Video Tutorial Scripts
- **File**: `training/VIDEO_TUTORIAL_SCRIPTS.md`
- **Duration**: 2 hours (8 videos)
- **Content**: Detailed scripts for video production
- **Best for**: Visual learners, self-paced

### 4. Certification Quiz
- **File**: `training/CERTIFICATION_QUIZ.md`
- **Duration**: 30 minutes
- **Content**: 20 questions, 80% to pass
- **Best for**: Knowledge assessment

---

## 🎓 Learning Paths

### Path 1: New Team Member (3 weeks)
```
Week 1: Foundation
├── Training Presentation
├── Exercises 1-2
├── Exercises 3-4
└── Certification Quiz

Week 2: Practice
├── Convert simple tests
├── Create page objects
└── Code review

Week 3: Advanced
├── Advanced features
├── CI/CD setup
└── Mentor others
```

### Path 2: Fast Track (3-5 days)
```
Day 1: Presentation + Exercises 1-2
Day 2: Exercises 3-4 + Convert test
Day 3: Certification + Start migration
```

---

## 📋 Exercise Overview

| Exercise | Topic | Duration | Difficulty |
|----------|-------|----------|------------|
| 1 | First Test | 30 min | Beginner |
| 2 | Page Objects | 45 min | Intermediate |
| 3 | Data-Driven | 45 min | Intermediate |
| 4 | Session Reuse | 30 min | Intermediate |
| Bonus | Tables | 30 min | Advanced |

---

## ✅ Certification Requirements

### To Get Certified:
1. Complete all exercises
2. Score 80%+ on quiz (16/20)
3. Convert 1 Java test to Python
4. Pass code review

### Certificate Benefits:
- Official recognition
- Mentor eligibility
- Advanced training access
- Framework contribution rights

---

## 🎬 Video Tutorial Topics

1. **Introduction** (10 min) - Framework overview
2. **Elements** (15 min) - Locators and interactions
3. **Page Objects** (20 min) - POM pattern
4. **Data-Driven** (15 min) - Parametrization
5. **Sessions** (10 min) - Save and restore
6. **Advanced** (20 min) - Tables, verification, config
7. **Migration** (25 min) - Java to Python
8. **CI/CD** (15 min) - Pipeline integration

---

## 💡 Key Concepts

### Must Know
- Async/await syntax
- Element locator strategies
- Fixture usage
- Page Object Model
- Session management

### Should Know
- Data-driven testing
- Soft assertions
- Table interactions
- Configuration management
- Error handling

### Nice to Know
- Property-based testing
- Visual regression
- Performance testing
- Custom reporters
- Advanced CI/CD

---

## 🔧 Setup Checklist

Before starting training:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] RAPTOR installed (`pip install raptor-playwright`)
- [ ] Browsers installed (`playwright install`)
- [ ] IDE configured (VS Code recommended)
- [ ] Test environment access

---

## 📞 Support Resources

### Documentation
- User Guide: `docs/USER_GUIDE.md`
- API Reference: `docs/API_REFERENCE_GUIDE.md`
- Migration Guide: `docs/MIGRATION_GUIDE_COMPREHENSIVE.md`

### Examples
- Basic: `examples/test_example_login.py`
- Data-Driven: `examples/test_example_data_driven.py`
- Page Objects: `examples/test_example_multi_page_workflow.py`

### Help Channels
- Chat: #raptor-support
- Email: test-automation-team@company.com
- Office Hours: Tuesdays 2-3 PM

---

## 🎯 Success Metrics

### Individual
- Complete training in 3 weeks
- Pass certification (80%+)
- Convert 5+ tests in first month
- Help train 1 team member

### Team
- 100% completion in 3 months
- 90%+ certification pass rate
- 50%+ maintenance time reduction
- 30%+ execution speed improvement

---

## 🚀 Quick Commands

### Installation
```bash
pip install raptor-playwright
playwright install
```

### Run Tests
```bash
pytest test_file.py -v
pytest -n 4  # Parallel
pytest --html=report.html  # With report
```

### Session Management
```bash
raptor session list
raptor session delete <name>
```

---

## 📝 Common Patterns

### Basic Test
```python
@pytest.mark.asyncio
async def test_example(page, element_manager):
    await page.goto("https://example.com")
    await element_manager.click("css=#button")
    assert await element_manager.is_visible("css=#result")
```

### Page Object
```python
class LoginPage(BasePage):
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.username = "css=#username"
        self.password = "css=#password"
    
    async def login(self, user, pwd):
        await self.element_manager.fill(self.username, user)
        await self.element_manager.fill(self.password, pwd)
```

### Data-Driven
```python
@pytest.mark.parametrize("user,pwd,expected", [
    ("valid", "pass123", True),
    ("invalid", "wrong", False),
])
async def test_login(page, element_manager, user, pwd, expected):
    # Test implementation
```

---

## ⚠️ Common Pitfalls

### Avoid These Mistakes
- ❌ Forgetting `async`/`await`
- ❌ Not using fixtures
- ❌ Hardcoded waits
- ❌ Not using page objects
- ❌ Ignoring error messages

### Best Practices
- ✅ Use meaningful names
- ✅ Keep tests independent
- ✅ Leverage session reuse
- ✅ Write reusable page objects
- ✅ Use soft assertions

---

## 📅 Training Schedule Template

### Week 1: Foundation
- **Monday**: Presentation (1 hour)
- **Tuesday**: Exercise 1 (1 hour)
- **Wednesday**: Exercise 2 (1.5 hours)
- **Thursday**: Exercise 3 (1.5 hours)
- **Friday**: Exercise 4 + Quiz (1.5 hours)

### Week 2: Practice
- Convert existing tests
- Create page objects
- Implement data-driven tests
- Code reviews

### Week 3: Advanced
- Advanced features
- CI/CD integration
- Performance optimization
- Team knowledge sharing

---

## 🏆 Certification Process

### Steps
1. Complete all exercises ✓
2. Take quiz (80%+ to pass) ✓
3. Convert 1 Java test ✓
4. Code review ✓
5. Receive certificate ✓

### Timeline
- Self-paced: 1-3 weeks
- Group training: 3 weeks
- Fast track: 3-5 days

---

## 📊 Progress Tracking

### Self-Assessment
- [ ] Completed presentation
- [ ] Finished Exercise 1
- [ ] Finished Exercise 2
- [ ] Finished Exercise 3
- [ ] Finished Exercise 4
- [ ] Passed certification quiz
- [ ] Converted first test
- [ ] Created page objects
- [ ] Implemented data-driven test
- [ ] Helped train someone

---

## 🎉 Next Steps After Certification

1. **Apply Skills**
   - Convert test suite
   - Create page object library
   - Set up CI/CD

2. **Advanced Learning**
   - Property-based testing
   - Visual regression
   - Performance testing

3. **Give Back**
   - Mentor new learners
   - Contribute to framework
   - Share best practices

---

## 📖 Additional Resources

### Internal
- Framework documentation
- Code examples
- Team wiki
- Support channels

### External
- Playwright docs: https://playwright.dev
- pytest docs: https://pytest.org
- Python docs: https://python.org

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2024  
**For**: RAPTOR Python Playwright Framework Training
