# Check `/tmp` Space Before Any Multi-Step Run

**A preflight check for any run that fetches, builds, or writes large files.**

> Found 2026-10-29 and again 2026-11-02. A research run died with
> `ENOSPC: no space left on device` **while writing its own web-fetch spill
> logs**. The failure looked like a web-fetch problem. It was a disk problem.
> **Last verified:** 2026-11-02 — `/tmp` measured at 100% with a 512 MB tmpfs,
> cleared to 27% by removing stale spill files and leftover virtualenvs.

## The Rule

> **Check `df -h /tmp` before debugging any tool that writes to `/tmp`. A
> full `/tmp` produces failures that name the wrong thing.**

## Why It Misleads

```
/tmp  tmpfs  512M  512M  0  100%  /tmp
```

A web-fetch provider that receives a response larger than its inline limit
spills the **full response** to `/tmp/openclaw-web-fetch-*.log`. Those files
are **never rotated**. A run that fetches twenty pages writes twenty spill
files, and nothing ever removes them.

The symptom lands in the middle of the fetch layer:

```
OSError: [Errno 28] No space left on device
```

...and it reads like the fetch failed. It did not fail. It ran out of room
**while writing the successful response.**

## The Culprits Are Accumulated, Not Current

On the first occurrence:

| what | how many | size |
|---|---|---|
| `openclaw-web-fetch-*.log` spill files | 163 | most of the 512 MB |
| abandoned virtualenvs (`py3.8venv`, `ruffenv`, `tc-venv`, `tse-deps`, ...) | 9 | the rest |

On the second occurrence, 23 more spill files plus leftover `/tmp/tmp*`
directories had filled it again within hours.

**Clearing them took `/tmp` from 100% to 27%.**

## The Procedure

```bash
# 1. Check first. Cheap, and it explains a whole class of mystery failures.
df -h /tmp

# 2. See what is there before deleting anything.
du -sh /tmp/* 2>/dev/null | sort -rh | head -20

# 3. Check that nothing is using a candidate directory.
ps -eo pid,args | grep -E 'venv|virtualenv|tmp' | grep -v grep

# 4. Clear the spill files (they are never rotated and never reused).
ls -la /tmp/openclaw-web-fetch-*.log 2>/dev/null
rm -f /tmp/openclaw-web-fetch-*.log

# 5. Verify.
df -h /tmp
```

## The Safety Rule Before Deleting A Directory

> **Before deleting a directory under `/tmp`, check that no process is using
> it.**

Directories named after a task (`ssenv`, `tse-deps`) look disposable but can
be a live CI sandbox. The check that makes the delete safe:

```bash
ps -eo pid,args | grep -E '/tmp/ssenv|/tmp/tse-deps' | grep -v grep
```

An empty result before the `rm -rf` is what makes the delete safe. **Run it
first, read it, then delete.**

## The Other Thing To Check

The container's root overlay matters too:

```
overlay  96G  82G  15G  86%  /
```

At 86% with 15 GB free, a run that also writes into the workspace is fine.
At 95%, a virtualenv build is not. `/tmp` filling is often the *first* symptom
of a disk problem, and it is the one that produces misleading error messages.

See also `prompts/go-build-on-tmpfs.md` (a tmpfs `/tmp` that breaks the Go
toolchain) and `skills/dev-env-defects/SKILL.md` (proving the environment before
reading a failure as a code defect).
