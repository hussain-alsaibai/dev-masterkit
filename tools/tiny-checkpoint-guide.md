# tiny-checkpoint — Zero-Dependency Checkpoint/Suspend/Resume for Long-Running Agents

**Repo:** github.com/hussain-alsaibai/tiny-checkpoint
**Install:** pip install tiny-checkpoint

> **Not published (verified 2026-11-03).** `pip install tiny-checkpoint` fails - the
> name returns **HTTP 404** on the PyPI JSON API. Install from the
> repository instead:
>
> ```bash
> pip install git+https://github.com/hussain-alsaibai/tiny-checkpoint.git
> ```
**Last verified:** 2026-08-14

Save state at arbitrary points, resume after crash, diff snapshots, capture dead-letter state. Auto-checkpoint decorator, incremental diffs, TTL, atomic JSON writes, thread-safe.
