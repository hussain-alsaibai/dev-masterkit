# Single-user mode is a local bypass of a remote auth model

**Last verified:** 2026-11-10

## The situation

Running a Python package's test suite in a scratch directory under `/tmp`
failed for every test that imported anything with a compiled extension:

```
ImportError: .../pydantic_core/_pydantic_core.cpython-311-x86_64-linux-gnu.so:
failed to map segment from shared object
```

`sqlalchemy`, `cryptography`, `pydantic_core`, `lxml`, `greenlet` — every
binary wheel, every time. **Pure-Python packages installed into the same
directory worked fine.** The failure looks like a broken wheel, a broken
interpreter, or a corrupted cache. It is none of those.

## What it actually is

`/tmp` on this host is a **tmpfs** and it is often at 87–100% before a test
run starts. A 512 MB filesystem hosting a 60 MB `.so` needs contiguous
addressable space at `mmap` time; when the tmpfs is full, `mmap` fails and
Python reports it as a malformed shared object.

The misleading part is the wording: **"failed to map segment" is an `ENOMEM`,
not a corrupt file.**

## How to tell it apart from a real wheel problem

| Observation | Means |
|---|---|
| every binary wheel fails, every pure-Python wheel works | tmpfs/memory, not the wheels |
| the same wheel installs fine under `$HOME` | same |
| `df -h /tmp` shows >90% | same |
| one wheel fails, others install | a real wheel problem |
| works after `rm -rf` of siblings, fails again later | pressure, so it will recur |

## The procedure

1. **Install anything with a `.so` outside `/tmp`** — `/home/node/<dir>` on
   this host. Test projects, virtualenvs, `--basetemp`, build trees.
2. **Purge shadowing re-installs.** `alembic` and `fastapi` re-pull
   `sqlalchemy` into the target, so a later install silently shadows a working
   one. After each install: `rm -rf <target>/sqlalchemy*` and re-run the
   import check.
3. **Check `df -h /tmp` before a long run**, not after it fails. Two clones
   were wiped mid-run by pressure in a single afternoon.
4. **Do not read the first failure as the diagnosis.** Read the *shape* of the
   failure set: a whole class of binaries failing with one error message is an
   environment signal.

## The generalisable rule

> **A dependency that installs but cannot be imported is a question about the
> destination, not about the dependency.** Ask which filesystem it landed on
> and how much room that filesystem has before asking whether the wheel is
> good.

This is the install-time sibling of the [full tempdir](../prompts/a-rerun-is-not-a-rerun-if-the-tempdir-was-full.md)
failure: one corrupts `tmpdir` during a test, the other corrupts `mmap`
during an install. Both arrive wearing a code problem's clothes.

## Counter-rule

Moving everything off `/tmp` hides the pressure rather than fixing it. A host
whose `/tmp` is permanently full will still fail some other way — logs,
sockets, or another agent's clone. Treat a recurring 90%+ `/tmp` as the bug.

## Verified

- Reproduced 2026-11-10 on this host: five binary wheels failed in `/tmp`,
  all five installed and imported under `/home/node/`.
- `df -h /tmp` at the time: `tmpfs 512M ... 0` available.
- The pure-Python packages installed into the identical directory in the same
  command, which is the control that rules out the wheels.
