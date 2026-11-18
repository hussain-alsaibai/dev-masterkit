# Test TMPDIR on a `noexec` mount

**Last verified: 2026-11-18** (this host: `/tmp` is `tmpfs ... noexec`; the repo
suite goes 8 failed → 301 passed moving `TMPDIR` off it).

## The 20-second diagnosis

When tests fail only on a fixture that writes and then executes something, check
the mount before the code:

```bash
mount | grep -E "noexec" | grep -E " /tmp | /dev/shm | $HOME "
```

```bash
python3 - <<'PY'
import os, tempfile
d = tempfile.mkdtemp(); p = os.path.join(d, "probe")
open(p, "w").write("#!/bin/sh\nexit 0\n"); os.chmod(p, 0o755)
print(oct(os.stat(p).st_mode), os.access(p, os.X_OK))
PY
```

- mode `0o100755` + `os.access(...) is False` → the mount forbids execution. The
  permission bits are irrelevant and `chmod` cannot fix it.
- mode fine + `os.access` True + still failing → the shebang's interpreter is
  missing, a different bug.

## Environment-only fix

```bash
mkdir -p "$HOME/tmp"
TMPDIR="$HOME/tmp" python3 -m pytest -q      # pytest's tmp_path honours TMPDIR
TMPDIR="$HOME/tmp" npm test                  # node os.tmpdir() honours it too
```

In containers, prefer setting `TMPDIR` in the image rather than per-command:
`ENV TMPDIR=/var/tmp/ci` in a Dockerfile, or `environment = { TMPDIR = ... }` in
CI config — a path that is writable *and* executable.

## What NOT to do

- **Do not relax the check.** Turning `os.access(p, os.X_OK)` into `os.path.isfile(p)`
  makes the test pass everywhere and stops testing the contract ("this path can be
  executed directly").
- **Do not invoke the stub through the interpreter** (`sys.executable, stub`) as a
  "portable" workaround. That proves the source is valid Python, not that the
  binary is executable — it silently stops covering the resolution order the
  script exists to implement.
- **Do not treat it as flaky and retry.** It reproduces 100% on that host and 0%
  on a normal one, which is the signature of an environment precondition, not
  nondeterminism.

## Where this bites in practice

- Any test spawning a file it just wrote: CLI stubs, shell shims, `gh`/`docker`
  fakes on `PATH`, Playwright wrappers, git hooks.
- `/tmp` on hardened Kubernetes/GKE nodes, `docker run --tmpfs /tmp:noexec`,
  and several CI sandboxes.
- `npm test` with a `postinstall` that builds a binary into a temp dir.
