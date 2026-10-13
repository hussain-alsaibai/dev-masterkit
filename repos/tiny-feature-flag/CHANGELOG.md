# Changelog

All notable changes to `tiny-feature-flag` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-13

### Added
- `Flag` dataclass: name, default, rules, overrides, description.
- `FlagStore`: thread-safe registry with `register`, `unregister`, `enabled`, `evaluate_all`.
- `Context` dataclass: `user`, `request`, `env`, `extra`, plus `get(path)` helper.
- `Rule` factories: `eq`, `ne`, `in_`, `contains`, `matches`, `percent`, `predicate`.
- Three-valued rule semantics: `True` enables, `False` forces off, `None` defers.
- Stable percentage rollouts via SHA-256 bucketing.
- 28 unit tests covering rules, flags, store, integration scenarios, thread-safety.
