# Probing Annotation Deferral Without A 3.8 Interpreter

**Last verified:** 2026-11-21

Deciding whether a module-level annotation is a runtime error on its declared
minimum Python needs the *arm that fails*, not only the arm that passes. This
script runs both, on whatever interpreter is present.

## The script

```python
#!/usr/bin/env python3
"""Two cases, one command. Asserts the plain arm FAILS, not just that the
future arm passes -- a probe that only checks the passing arm cannot tell a
deferred annotation from a probe that never ran."""
import os, subprocess, sys, tempfile

def run(with_future: bool):
    d = tempfile.mkdtemp(dir=os.path.expanduser("~/tmp"))
    p = os.path.join(d, "probe_mod.py")
    with open(p, "w") as fh:
        if with_future:
            fh.write("from __future__ import annotations\n")
        fh.write("X: NOEXIST = 1\n")
    r = subprocess.run([sys.executable, "-c", "import probe_mod"],
                       cwd=d, capture_output=True, text=True)
    return r.returncode, (r.stderr.strip().splitlines() or [""])[-1]

fails = []
code, err = run(False)
print(f"no future import   -> rc={code} {err}")
if code == 0:
    fails.append("plain arm imported: deferral cannot be distinguished")
code, err = run(True)
print(f"WITH future import -> rc={code} {err}")
if code != 0:
    fails.append(f"future arm raised: {err}")
sys.exit(1 if fails else 0)
```

## Verified output (2026-11-21, Python 3.11.2)

```
no future import     -> rc=1 NameError: name 'NOEXIST' is not defined
WITH future import   -> rc=0
```

## Why a nonexistent name, and not `dict[str, int]`

`dict[str, int]` is a real expression on 3.9+, so it proves nothing on the
interpreter you are already running. An unresolvable **name** is the difference
between "evaluated" and "deferred" on every version, and it fails loudly in the
arm you want to fail.

## Host note

`/tmp` on this container is `noexec`, so the probe writes under
`$HOME/tmp` (`tempfile.mkdtemp(dir=os.path.expanduser("~/tmp"))`). Same
constraint as `tools/test-tmpdir-on-a-noexec-mount.md`.

## Reading the verdict

| plain arm | future arm | meaning |
|---|---|---|
| fails | passes | annotations deferred — PEP 585 at module level is safe |
| fails | fails | the future import is missing or not first statement |
| passes | passes | probe is broken; the annotation is not being evaluated at all |

## Related

- `prompts/a-future-import-hides-the-error-the-syntax-check-accepts.md`
- `prompts/python-support-is-a-claim.md`
