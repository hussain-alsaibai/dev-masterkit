# Spec Literals Must Be Generated, Not Hand-Copied

**A rule for writing tests against an exact specification.**

> Found 2026-10-25 while writing tests for
> `pipeshub-ai/pipeshub-ai#4650` (`url_redaction.redact_urls_in_text`).
> The tool output layer redacts secret-looking strings, so `token=secret`
> arrived as `token=***`. A hand-typed test would have asserted against a
> different string than the issue pinned. **Last verified:** 2026-10-25 —
> every literal in the finished file was checked byte-for-byte against the
> spec.

## The Failure Mode

You read a specification that pins exact strings. You write a test. You
type the strings from what you read. The test passes.

**That is exactly the problem.** The test passed against *your transcription
of the spec*, not against the spec.

The gap is invisible in the happy path. It becomes visible only when the
value being asserted is one the pipeline might rewrite on the way to you:

- secret-looking values (`token=secret`, `api_key: hunter2`, `password=`)
- long URLs with embedded credentials
- anything matching a redaction pattern in the tool/output layer

When the transport redacts a value, **the reader gets a different value than
the one in the document**. The redaction is correct in its own context — it
protects secrets — and catastrophic in this one: it silently rewrites the
specification you are testing against.

## The Rule

> **If the spec pins an exact literal, the test must read that literal from
> the spec at runtime. Never retype it.**

```python
# WRONG — hand-transcribed, and silently different from the spec
def test_redacts_token():
    assert redact_urls_in_text("token=secret") == "token=***"

# RIGHT — the literal comes from the spec, so it cannot drift
import re, pathlib

SPEC = pathlib.Path("issue-4650.md").read_text()   # fetched at runtime

def test_redacts_token():
    literal = extract_case(SPEC, "redacts_token")   # the exact bytes
    assert redact_urls_in_text(literal) == expected(SPEC, literal)
```

The generator fetches the issue body at test time, parses the pinned case,
and writes the **exact bytes** into the test file. The literal in the test
is then byte-identical to the one in the spec — verifiable, and
re-verifiable:

```bash
# every literal in the test file must appear byte-identically in the spec
```

## Why "It Passed" Is Not Evidence

A test that passes proves that the code agrees with the test. It does not
prove the test agrees with the spec. When the test's source of truth is a
human's typing, the chain of custody is broken at exactly one point — and
that point is the one nobody checks.

This is the same failure the sibling guide `prompts/readme-claims-must-be-runnable.md`
warns about from the other direction: there, the doc drifted from the code;
here, the test drifted from the spec.

## The Cheaper Alternative

If fetching the spec at runtime is impractical (offline CI, a spec that
lives in a chat message), then **generate the test file from the spec once
and commit the generated output** — but generate it with a script, not with
your hands, and keep the generator next to the test so the test can be
regenerated on demand.

```
spec.md  ->  gen_tests.py  ->  test_xxx.py
```

Hand-writing the generator is more work up front and much less work later,
because the second issue on the same spec costs one command instead of an
evening.

## The Generalisation

> **Any value that travels through a system that may rewrite it must be
> transported, not transcribed.** Transcription adds a copy step, and copy
> steps are where correctness leaks. If a pipeline redacts, normalises,
> truncates, or formats, then a value that passes through it must be
> compared against the *original*, at the point where the original is still
> available.

This applies to:

- API responses you must echo byte-for-byte,
- file contents compared across a copy,
- hashes or checksums of a payload,
- CLI output asserted in a golden test.

See also `prompts/mutation-test-proves-the-test.md` — a green test proves
nothing until it has been shown to fail against the bug it guards.
