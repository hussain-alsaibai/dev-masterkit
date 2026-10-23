# tiny-pipeline Guide

## Repo
https://github.com/hussain-alsaibai/tiny-pipeline

## What It Does

Zero-dependency streaming data pipeline for Python. One file, no setup. Chained
processing stages with a sync and an async variant.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_pipeline import
Pipeline, source, sink`. **There are no `source` or `sink` helpers.** Verified
against upstream `tiny_pipeline.py`:

```
__all__ = ['Pipeline', 'AsyncPipeline', 'PipelineStats']
```

`Pipeline` is the sync pipeline, `AsyncPipeline` the async variant, and
`PipelineStats` carries the counters.

## Quick Start

```python
from tiny_pipeline import Pipeline

p = Pipeline()
p.add_stage("parse", lambda raw: raw.splitlines())
p.add_stage("count", lambda lines: len(lines))

result = p.run(raw_text)
print(p.stats.processed)
```

## When to Use

- Chaining pure transformations over a stream of items
- Needing stage-level stats without a framework
- The async variant, when stages perform I/O

## Related

- `tools/tiny-workflow-guide.md` — DAG orchestration with retries and approval gates
- `tools/tiny-watch-guide.md` — file watching that can trigger a pipeline
