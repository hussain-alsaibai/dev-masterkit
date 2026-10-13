## [0.2.0] - 2026-10-13

### Added
- `compare_models(models, *, system, user, history, expected_completion, tools_tokens, safety_margin, cost_per_million, model_limits)`
  runs `plan()` across many models and returns a list of
  `(model, Budget, estimated_cost_usd_or_None)` tuples sorted by
  `fits` (desc), then `remaining` (desc), then `cost` (asc).
- `COST_PER_MILLION` catalogue: USD per 1M input/output tokens for
  the 2026-Q4 frontier set (OpenAI, Anthropic, Google, Meta, Mistral,
  DeepSeek). Mutable at runtime; pass your own dict to
  `compare_models(cost_per_million=...)` to override.
- 10 new tests in `test_tiny_llm_budget_v020.py` covering compare,
  cost estimation, input/output split, history-as-input, sorting,
  and the cost catalogue invariants.
# Changelog

All notable changes to `tiny-llm-budget` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-12

### Added
- Initial public release. ~290 LOC, zero required dependencies.
- `count_tokens(text, model)` with three strategies:
  - `tiktoken` for OpenAI models (when installed)
  - 3.5 chars/token + 1.1x safety for Anthropic models
  - 4 chars/token + 1.15x safety for everyone else
- `plan(model, *, system, user, history, expected_completion, tools_tokens, safety_margin, model_limits)`
  returns a `Budget` dataclass with `fits`, `total_tokens`,
  `remaining`, `segments`, and `strategy`.
- `Budget` and `Segment` dataclasses (frozen, JSON-serializable
  via `to_dict()`).
- 2026-Q4 model catalogue: gpt-4o / 4o-mini / 4-turbo / 4 /
  3.5-turbo, o1-preview / o1-mini, claude-3-5-{sonnet, haiku} /
  3-{opus, sonnet, haiku}, gemini-1.5-{pro, flash} / 2.0-flash-exp,
  llama-3.1-{405b, 70b, 8b}, mistral-large-2, mixtral-8x22b,
  deepseek-v3. Unknown models default to 8k.
- `register_model(name, max_tokens)` for fine-tunes and self-hosted
  endpoints.
- 18 tests covering token counting, model limits, plan
  computation, segments, overflow, safety margin, custom limits,
  tool tokens, JSON serialisation, and strategy selection.
