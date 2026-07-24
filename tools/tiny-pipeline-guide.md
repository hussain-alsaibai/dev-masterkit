# tiny-pipeline Guide

**Repo:** [hussain-alsaibai/tiny-pipeline](https://github.com/hussain-alsaibai/tiny-pipeline)  
**Size:** ~1300 LOC | **Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> UNIX pipes, but for Python iterators. With async.

## What it does

A tiny, zero-dependency streaming data pipeline builder. Chain sources, transforms, and sinks using Python iterators — with native async support.

## When to use

- **ETL pipelines** that need to process large datasets without loading everything into memory
- **Streaming AI pipelines** — chunk documents, process with LLM, store results
- **Data transformation chains** — filter, map, reduce on large iterables
- **Async data flows** — WebSocket streams → transform → database writes

## Key patterns

```python
from tiny_pipeline import Pipeline, source, sink, step

pipe = (
    Pipeline()
    .source(my_generator)
    .step(filter_fn)
    .step(transform_fn)
    .sink(save_fn)
)
pipe.run()
```

## Related

- `tiny-chain` — LLM processing chain, can feed into pipeline for structured output handling
- `tiny-workflow` — DAG orchestration for multi-step workflows with retry/approval gates
- `tiny-eventbus` — durable event streams, can serve as pipeline source or sink
