# HTML Report Preview

## Report Structure

The RAPTOR HTML test report consists of three main sections:

### 1. Header Section
```
┌─────────────────────────────────────────────────────────┐
│  RAPTOR Test Report                                     │
│  Example Test Suite - Login Module                      │
│  Generated: 2024-01-15 10:30:00                        │
└─────────────────────────────────────────────────────────┘
```
- Gradient purple background
- White text
- Suite name and timestamp

### 2. Summary Section
```
┌─────────────────────────────────────────────────────────┐
│  Test Summary                                           │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │    6     │ │    3     │ │    1     │ │    1     │ │
│  │  Total   │ │  Passed  │ │  Failed  │ │ Skipped  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │    1     │ │  2.03s   │ │  50.0%   │              │
│  │  Errors  │ │ Duration │ │Pass Rate │              │
│  └──────────┘ └──────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────┘
```
- Color-coded cards:
  - Total: Blue
  - Passed: Green
  - Failed: Red
  - Skipped: Orange
  - Errors: Pink
  - Duration: Purple
  - Pass Rate: Teal

### 3. Test Results Section
```
┌─────────────────────────────────────────────────────────┐
│  Test Results                                           │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ ✓ Test Valid Login with Correct Credentials    │  │
│  │                                        2.50s  ▼ │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ ✗ Test Login with Invalid Password             │  │
│  │                                        1.20s  ▼ │  │
│  │ ┌───────────────────────────────────────────┐  │  │
│  │ │ Test ID: TC_002                           │  │  │
│  │ │ Start Time: 2024-01-15 10:30:02          │  │  │
│  │ │ End Time: 2024-01-15 10:30:03            │  │  │
│  │ │ Duration: 1.20s                          │  │  │
│  │ │                                          │  │  │
│  │ │ Error Message:                           │  │  │
│  │ │ AssertionError: Expected 'test' got 'prod'│  │  │
│  │ │                                          │  │  │
│  │ │ Stack Trace:                             │  │  │
│  │ │ Traceback (most recent call last):      │  │  │
│  │ │   File "test.py", line 10                │  │  │
│  │ │     assert value == 'test'               │  │  │
│  │ │                                          │  │  │
│  │ │ Screenshots:                             │  │  │
│  │ │ [📷 error.png]                           │  │  │
│  │ │                                          │  │  │
│  │ │ Metadata:                                │  │  │
│  │ │ browser: chromium                        │  │  │
│  │ │ environment: staging                     │  │  │
│  │ └───────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ ⊘ Test Password Reset Email                    │  │
│  │                                        0.00s  ▼ │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Color Scheme

### Status Colors
- **Passed (✓)**: Green (#4caf50)
- **Failed (✗)**: Red (#f44336)
- **Skipped (⊘)**: Orange (#ff9800)
- **Error (⚠)**: Pink (#e91e63)

### Background Colors
- **Header**: Purple gradient (#667eea → #764ba2)
- **Summary Cards**: Light pastels matching status colors
- **Test Results**: White with colored left border
- **Error Sections**: Light red background (#fff5f5)

## Interactive Features

### 1. Expandable Test Details
```
Click on test header → Details expand/collapse
                     → Arrow icon rotates
```

### 2. Screenshot Modal
```
Click on screenshot → Opens full-size modal
                    → Dark overlay background
                    → Click anywhere to close
                    → Press ESC to close
```

### 3. Hover Effects
```
Hover on test header → Background changes to light gray
Hover on screenshot  → Image scales up slightly
Hover on close icon  → Color changes
```

## Responsive Design

### Desktop (> 1200px)
- Full-width layout with max-width container
- 7 statistics cards in grid
- Multiple screenshots per row

### Tablet (768px - 1200px)
- Responsive grid adjusts
- 3-4 cards per row
- 2-3 screenshots per row

### Mobile (< 768px)
- Single column layout
- Stacked statistics cards
- Single screenshot per row
- Touch-friendly interactions

## Typography

### Fonts
- Primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- Monospace: 'Courier New', monospace (for code/errors)

### Sizes
- Header H1: 2.5em
- Header H2: 1.5em
- Section H3: 1.2em
- Body: 1em (16px base)
- Small: 0.9em

## Example HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>RAPTOR Test Report</title>
    <style>/* Modern CSS styles */</style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>RAPTOR Test Report</h1>
            <h2>Suite Name</h2>
            <p class="timestamp">Generated: ...</p>
        </header>
        
        <!-- Summary -->
        <section class="summary">
            <h3>Test Summary</h3>
            <div class="stats-grid">
                <div class="stat-card total">...</div>
                <div class="stat-card passed">...</div>
                <!-- More cards -->
            </div>
        </section>
        
        <!-- Test Results -->
        <section class="test-results">
            <h3>Test Results</h3>
            <div class="test-result passed">
                <div class="test-header">...</div>
                <div class="test-details">...</div>
            </div>
            <!-- More results -->
        </section>
    </div>
    
    <!-- Screenshot Modal -->
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>
    
    <script>/* Interactive JavaScript */</script>
</body>
</html>
```

## Accessibility Features

- ✅ Semantic HTML structure
- ✅ ARIA labels where appropriate
- ✅ Keyboard navigation support
- ✅ High contrast colors
- ✅ Readable font sizes
- ✅ Clear visual hierarchy
- ✅ Focus indicators

## Browser Compatibility

- ✅ Chrome/Chromium (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

## File Size Considerations

### Without Embedded Screenshots
- Typical size: 50-200 KB
- Fast loading
- External screenshot files

### With Embedded Screenshots
- Typical size: 500 KB - 5 MB
- Self-contained
- No external dependencies
- Larger file size

## Best Practices

1. **Use embedded screenshots for:**
   - Archival purposes
   - Sharing single file
   - Email attachments

2. **Use linked screenshots for:**
   - Large test suites
   - Many screenshots
   - Faster loading
   - Smaller file size

3. **Optimize screenshots:**
   - Use PNG for UI screenshots
   - Compress images before adding
   - Limit screenshot dimensions
   - Clean up old screenshots

## Customization Options

The HTML report can be customized by:
- Extending the TestReporter class
- Overriding `_get_css_styles()` method
- Modifying color scheme
- Adding custom sections
- Changing layout structure

## Example Customization

```python
class CustomReporter(TestReporter):
    def _get_css_styles(self):
        # Return custom CSS with your branding
        return """
        header {
            background: linear-gradient(135deg, #your-color1, #your-color2);
        }
        /* More custom styles */
        """
```

## See Also

- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
- [Quick Reference](REPORTER_QUICK_REFERENCE.md)
- [Examples](../examples/reporter_example.py)
