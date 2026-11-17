# A default-value marker is resolved through its binding, not its name

**Discovered:** 2026-11-17 (`tiny-cli` 1.3.2, `option("--user")` on `def show(user_id)`)
**Last verified:** 2026-11-17 — 10 new tests in `test_v131_option_dest.py`, **5 of which
fail on the unfixed module**; `tiny-cli` 143 passed, CI `44089048407` green on 3.9–3.13;
shipped at `1942a7b`.

## The claim

A framework marker used as a parameter default carries **two** names: the name it
declares (`--user`) and the name of the parameter it is assigned to (`user_id`). If the
framework reads only the first, the second is never bound — and nothing raises.

## The reproducer

```python
@cli.command()
def show(user_id: str = tc.option("--user", default="1")):
    return {"id": user_id}
```

```console
$ myapp show --user 9 --json
{"result": {"id": {"_kind": "option", "flags": ["--user"], "default": "1", ...}}}
```

The flag was parsed. The value was discarded.

The builder handed the flags straight to argparse:

```python
sub.add_argument(*m["flags"], type=..., help=..., default=...)
```

argparse derives `dest` from the first long flag — `--user` becomes `user`. The dispatcher
then looked the parameter up by its **name**:

```python
if hasattr(args, pname):        # pname == "user_id", dest == "user"
    kwargs[pname] = getattr(args, pname)
```

`hasattr` was `False`, so the parameter was never bound.

## Two outcomes, both silent

| author wrote | command received |
|---|---|
| `--user 9` supplied | the marker default `"1"` |
| flag omitted | the raw marker **dict** |

The second row is the one that reaches production, because a default is the common case.
In JSON mode the dict serialised straight into `result`; in text mode it was interpolated
into a string nobody compared.

**Fix:** `add_argument(..., dest=pname)` on both the `store_true` and the typed form. The
flag name is then free to differ from the parameter name — which is the reason to have
both.

## Why 57 tests missed it

Every existing use in the suite used a matching name:

```python
times: int = tc.option("--times", default=1, type=int)
```

That is the single case where argparse's derived `dest` is already correct. The bug needed
a caller who named the flag differently from the parameter — the normal way to write
`--user` for `user_id`.

## The rule

> **A default-value marker must be resolved through the parameter it is assigned to,
> never through the name it declares.** Any framework that reads a descriptor's own name
> must map that name back to the binding site, and the test suite must contain at least
> one case where the two names differ.

## The two bugs found while writing the docs

Both were in the same code path and both were invisible until a documented example was
executed:

1. **An option with no default was optional.** `tc.option("--text")` carries
   `default=Ellipsis`; the builder dropped it and registered the flag with no default,
   which argparse reads as *optional*. Omitting the flag ran the command with the
   descriptor dict as the value. No `default=` written by the author now means
   `required=True` — verified by exit code 2 on a missing flag.
2. **A parse error corrupted the JSON envelope.** argparse writes its usage line to
   stdout on some error paths; JSON mode owns stdout, so `jq` failed on the usage line
   while the shell exit code came from `jq`, not from the app. stdout is now redirected
   during the parse and the usage line is re-emitted **inside** the envelope's `error`
   field — relocated, not dropped.

## Test shape that catches it

```python
def test_option_flag_name_differs_from_parameter_name():
    # must assert the VALUE, not that the flag parsed
    assert run("show", "--user", "9")["result"]["id"] == "9"

def test_option_omitted_uses_the_marker_default():
    assert run("show")["result"]["id"] == "1"      # not a dict

def test_option_never_serialises_the_marker():
    assert "_kind" not in json.dumps(run("show"))
```

The third assertion is the cheap one that catches every future variant: a marker object
must never reach output.

Last verified 2026-11-17 (5 of 10 new tests fail on the unfixed module; suite 143 passed
on 3.9–3.13).
