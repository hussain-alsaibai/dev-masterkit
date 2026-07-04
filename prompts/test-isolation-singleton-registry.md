# test-isolation-singleton-registry — Prompt for Singleton/Registry Test Patterns

## Description

Steers an agent debugging "DuplicateMetric" / "DuplicateFlag" / "AlreadyRegistered" /
"Counter was already created" errors in tests toward the right fix: per-test fixture
isolation, not module-level mutation. Common pattern across `tiny-metrics`,
`tiny-flags`, and any registry-based library.

## The Prompt

```
Tests are failing with "already registered", "duplicate name", or "metric already
exists" errors — usually on the second test that constructs a Counter/Flag/Router
with the same name. The root cause is a module-level singleton registry.

Diagnosis (run these in order):

1. **Identify the singleton.** Look for module-level mutable state in the library:
   - `REGISTRY = {}`
   - `_counters = []`
   - `_schedulers = []`
   - any module-level `dict`/`list`/`set`
2. **Confirm the singleton is the cause.** Run a single test in isolation:
   `pytest test_foo.py::test_bar -v` — if it passes alone and fails alongside
   another test, the singleton is leaking.
3. **Pick ONE of three isolation patterns.** Don't mix them; consistency wins:
   - **Per-test new instance.** Every test gets `fresh = make_registry()`.
     Use when the registry is small and the library exposes a constructor.
   - **Per-test reset fixture.** A pytest fixture calls `REGISTRY.clear()`
     before each test. Use when the library uses a hard-coded global.
   - **Per-test unique names.** Each test generates a unique name
     (`uuid.uuid4().hex[:8]`). Use when there's no way to inject a registry.

Implementation:

    # Option A — per-test new instance (preferred)
    def test_counter_increments(self):
        reg = fresh_registry()
        c = Counter("foo", "help", registry=reg)
        c.inc()
        assert c.value == 1

    # Option B — per-test reset fixture
    @pytest.fixture(autouse=True)
    def _reset():
        REGISTRY.clear()
        yield
        REGISTRY.clear()

    # Option C — per-test unique names
    def test_counter(self):
        name = f"foo_{uuid.uuid4().hex[:8]}"
        c = Counter(name, "help")
        ...

4. **Add a regression test.** Write `test_registry_isolation()` that constructs
   two metrics with the same name in sequence and asserts no collision.

Reporting:
- Show before/after of the failing test name.
- Note which isolation pattern you chose and why.
- Add the pattern to the library's CONTRIBUTING.md if missing.

Anti-patterns to avoid:
- Hiding the singleton behind lazy `_get_registry()` — same problem, harder to debug.
- Random sleep in tests — flaky, not isolation.
- Mocking the registry away — defeats the point of integration tests.
```

## When to Use

- Tests fail with "duplicate X" / "already registered" errors only when run as a suite
- Library has module-level `REGISTRY` / `_instances` / `_seen`
- Two tests both create `Counter("foo", ...)` or `FeatureFlag("foo", ...)`
- A new commit to a library broke previously-passing tests

## Anti-Triggers

- Tests fail in isolation too — not a singleton issue, look at the actual code
- Singleton is intentional (e.g. `random.Random()` — module-level is fine)
- Tests use `unittest.mock` to bypass the singleton already — check why it's mocked first

## Last Verified: 2026-07-04