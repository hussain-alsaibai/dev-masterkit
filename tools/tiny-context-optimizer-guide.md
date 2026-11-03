# tiny-context-optimizer — LLM Context Window Optimizer

## Repo
https://github.com/hussain-alsaibai/tiny-context-optimizer

## One-liner
Zero-dependency context pruning tool for AI agents. Deduplicates lines, cleans whitespace,
extracts signal from noise. ~50 LOC. MIT.

## Install
```bash
pip install tiny-context-optimizer
# Or: copy tiny_context_optimizer.py directly
```

> **Not published (verified 2026-11-03).** `pip install tiny-context-optimizer` fails - the
> name returns **HTTP 404** on the PyPI JSON API, and there is no GitHub
> repository under this name either. Copy the single file into your
> project instead.

## Quick Example
```python
from tiny_context_optimizer import TinyContextOptimizer

opt = TinyContextOptimizer()
lean = opt.prune_redundancy(large_context_string)
# Also: extract_signals(), truncate_to_token_budget()
```

## Key Features
- Line deduplication (fuzzy + exact)
- Whitespace normalization
- Signal extraction (Errors, Notes, TODOs)
- Token-aware truncation (planned)
- Zero dependencies

## Last Verified
2026-09-01
