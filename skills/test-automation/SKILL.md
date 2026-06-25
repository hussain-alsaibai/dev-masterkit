# test-automation — Skill for Auto-Generating Test Suites

## Trigger

Use when the user asks to:
- "Write tests for [file/function]"
- "Generate test suite"
- "Add unit tests"
- "Improve test coverage"
- "Create pytest tests" (convert to stdlib unittest)

## Description

Generates comprehensive, meaningful test suites using only Python's standard
library `unittest`. No external test frameworks required. Tests are deterministic,
fast, and cover happy path, edge cases, and error conditions.

## Procedure

### 1. Analyze Target Code

Read the module/function to test. Identify:
- Public functions/classes and their signatures
- Return types and possible values
- Side effects (file I/O, network, state mutation)
- Error conditions (TypeError, ValueError, FileNotFoundError, etc.)

### 2. Determine Test Strategy

| Code Characteristic | Testing Approach |
|---------------------|------------------|
| Pure functions (no I/O) | Direct assertion on return values |
| File I/O | Use `tempfile` + `setUp`/`tearDown` |
| Network calls | Mock with `unittest.mock` |
| State mutation | Capture before/after state in test |
| Random/cryptographic | Use fixed seeds where possible |

### 3. Generate Test File

Naming: `tests/test_{module_name}.py` or `test_{feature}.py`

Structure:
```python
import unittest
from {module} import {function_or_class}

class Test{Feature}(unittest.TestCase):
    def setUp(self):
        """Shared fixtures."""
        pass

    def test_{happy_path_description}(self):
        """Test normal operation with valid inputs."""
        pass

    def test_{edge_case_description}(self):
        """Test boundary conditions."""
        pass

    def test_{error_condition_description}(self):
        """Test raises appropriate exceptions."""
        pass

    def tearDown(self):
        """Cleanup temporary files, etc."""
        pass

if __name__ == "__main__":
    unittest.main()
```

### 4. Test Categories (generate at least 3 per function)

**Happy Path:**
- Typical inputs with expected outputs
- Default parameter values

**Edge Cases:**
- Empty inputs ("", [], {}, 0, None where valid)
- Boundary values (max int, zero, single-item collections)
- Unicode, special characters
- Very large inputs (if applicable)

**Error Conditions:**
- Wrong types (pass int where str expected)
- Invalid values (negative where positive required)
- Missing required arguments
- Resource not found (files, URLs)

**State & Side Effects:**
- Before/after state verification
- Idempotency (running twice same as once)
- Cleanup verification

### 5. Mock External Dependencies

Use `unittest.mock` for:
- `datetime.now()` → `unittest.mock.patch`
- HTTP requests → `unittest.mock.patch("urllib.request.urlopen")`
- File system → `tempfile.TemporaryDirectory` + real files
- Environment variables → `unittest.mock.patch.dict("os.environ")`

Example:
```python
from unittest.mock import patch, MagicMock

@patch("mymodule.urlopen")
def test_fetch_data(self, mock_urlopen):
    mock_urlopen.return_value = MagicMock(read=lambda: b'{"key": "value"}')
    result = fetch_data("https://api.example.com")
    self.assertEqual(result, {"key": "value"})
```

### 6. Run and Verify

```bash
python -m unittest discover -v
python -m unittest tests.test_{module} -v
```

Fix any failures before declaring complete.

## Example

**User:** "Write tests for a function `parse_date(date_str: str) -> datetime.date`"

**Generated `test_parse_date.py`:**
```python
import unittest
from datetime import date
from mymodule import parse_date

class TestParseDate(unittest.TestCase):
    def test_iso_format(self):
        self.assertEqual(parse_date("2024-03-15"), date(2024, 3, 15))

    def test_us_format(self):
        self.assertEqual(parse_date("03/15/2024"), date(2024, 3, 15))

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            parse_date("")

    def test_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            parse_date("not-a-date")

    def test_none_raises(self):
        with self.assertRaises(TypeError):
            parse_date(None)
```

## Validation Checklist

- [ ] All public functions/classes have corresponding test classes
- [ ] Each test has a descriptive docstring
- [ ] Tests run in isolation (no shared mutable state)
- [ ] External dependencies are mocked
- [ ] At least one test per: happy path, edge case, error condition
- [ ] `python -m unittest discover` passes with 100% success
- [ ] No external test dependencies (pytest, etc.)

## Notes

- Use `subTest()` for parameterized-like tests in unittest
- Keep tests fast (< 1 second total for unit tests)
- Group related tests in the same class; separate classes for unrelated modules
- Test file structure mirrors source structure: `src/foo/bar.py` → `tests/test_bar.py`
