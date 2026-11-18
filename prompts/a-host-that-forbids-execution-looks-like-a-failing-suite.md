# A host that forbids execution looks like a failing suite

**Last verified: 2026-11-18** — reproduced in this repository, 8 failures → 301 passed
with one environment variable. Suite: `tests/test_scan_skills.py` (301 tests total).

## The reading

```console
$ python3 -m pytest -q
FAILED tests/test_scan_skills.py::test_local_venv_beats_path - SystemExit: 1
FAILED tests/test_scan_skills.py::test_report_from_a_different_scanner_fails
8 failed, 293 passed
```

```console
$ python3 -m pytest -q
AssertionError: assert 'does not match the baseline' in
  'FAIL: SKILLSPECTOR_BIN=/tmp/pytest-of-node/pytest-28/test_version_drift_stops_the_s0/skillspector
   is not an executable file'
```

Eight tests, one message, one directory: `pytest`'s `tmp_path` is `/tmp`. This
container mounts `/tmp` `noexec`:

```
tmpfs on /tmp type tmpfs rw,nosuid,nodev,noexec,relatime,size=524288k
```

The fixture writes a scanner stub and does `os.chmod(path, 0o755)`. The mode is
`0o100755` on disk. `os.access(path, os.X_OK)` returns **False** anyway, because
`access(2)` on `noexec` denies execution regardless of the mode bits.

## Why this is a trap

1. **The failure is real but the diagnosis is wrong.** Nothing is broken in the
   code under test. Reading the assertion (`"does not match the baseline"` not
   in output) invites a fix to `scan_skills.py`. The script was correct: it
   refused a file it genuinely could not execute.
2. **It is silent on CI.** CI usually has an executable `/tmp`, so the same tree
   is green there. The failure only exists on one host, which reads as flaky.
3. **`chmod` succeeding proves nothing.** `os.chmod` returned 0. `stat` shows
   the bits set. Only `os.access(X_OK)` — or an actual `execve` — tells the truth.

## The check

```python
import os, tempfile
d = tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or "/tmp")
p = os.path.join(d, "probe")
open(p, "w").write("#!/bin/sh\nexit 0\n")
os.chmod(p, 0o755)
print("executable:", os.access(p, os.X_OK))
```

`executable: False` on an `noexec` mount. Cross-check with `mount | grep noexec`
rather than assuming the flag.

## The fix

Point the test session's scratch space at a filesystem that permits execution:

```console
$ TMPDIR=$HOME/tmp python3 -m pytest -q
301 passed in 2.83s
```

`pytest`'s `tmp_path` honours `TMPDIR`, so no test code changes. The alternative
— running the stub through an interpreter instead of `execve` — would weaken
what the test proves: the script's contract is "this path is directly
executable", and executing via `sys.executable stub.py` tests a different thing.

## The general rule

**A test harness that provisions an executable dependency must verify the host
will run it, or fail with a message that names the host.** An `EACCES`-shaped
failure raised from a fixture and surfaced as an assertion mismatch is a
misattribution: it points at the subject under test when the environment is the
defect. The same `noexec` flag is commonly set on `/tmp`, `/dev/shm` and CI
sandbox layers.

Note that this is the **inverse** of the unframed-response finding: there, a
green suite hid a defect because the layer was never exercised; here, a red
suite reports a defect in a layer that was never the subject. Both come from
the harness measuring at the wrong boundary.
