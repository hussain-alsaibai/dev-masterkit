# A Module That Cannot Be Imported Is Not A Library

**A rule for any package, module, or published library: importability is a
test, and it is the cheapest one you can write.**

> Found 2026-11-04. `tiny-mq` shipped version **1.0.0** with
> `import tiny_mq` raising:
>
> ```
> File "tiny_mq.py", line 448, in AsyncMessageQueue
>   self, topic: str, handler: Callable[[Message], Coroutine]
> NameError: name 'Coroutine' is not defined
> ```
>
> `Coroutine` was never imported. The annotation is evaluated at
> **class-definition time**, so the error fires before any of the library can
> run. The repo had a README, a LICENSE and a version. **It could not be
> imported at all.**
> **Last verified:** 2026-11-04 — reproduced by importing the published
> `main` branch of `tiny-mq`; `Coroutine` now comes from
> `collections.abc` (not `typing`, which has been deprecated since 3.9),
> and the module imports cleanly on 3.8, 3.11 and 3.13.

## The Rule

> **A repo with no tests and no CI can publish a module that does not
> import. `import <module>` in a test is the cheapest possible guard, and
> it catches the worst class of bug there is.**

The module does not need a feature to be broken. It needs one name that was
never imported, and that is enough to make the entire library unusable while
every other signal — README, badge, version — says it is fine.

## Why This Class Of Bug Is Invisible

The failure happens at **class-definition time**, which means:

| when | what happens |
|---|---|
| import time | the module never finishes loading |
| first use | never reached — the import failed first |

So there is no partial function, no degraded mode, and no error message
that names the feature you were trying to use. **You get a `NameError` about
a name you have never heard of**, pointing at a line you did not write.

## The Procedure

1. **Put the import in the test suite.** Not in a helper, not in a fixture
   — at the top level, where a failure is impossible to misread:

   ```python
   def test_module_imports():
       import tiny_mq  # noqa: F401
   ```

2. **Assert a real public API exists.** An import that succeeds on an empty
   module is not enough:

   ```python
   def test_has_public_api():
       import tiny_mq
       public = [n for n in dir(tiny_mq) if not n.startswith("_")]
       assert len(public) > 3
   ```

3. **Assert a version is declared somewhere a consumer can read it** —
   module-level `__version__` **or** packaging metadata. Four of our
   modules declared no version anywhere, and a consumer could not tell what
   they had installed.

   ```python
   def test_a_version_is_declared_somewhere():
       import tiny_mq
       meta = importlib.metadata.metadata("tiny-mq")
       assert getattr(tiny_mq, "__version__", None) or meta["Version"]
   ```

4. **Run the import from OUTSIDE the source tree.** From inside the repo
   the loose `.py` file shadows the installed package, and a wheel that
   ships nothing importable looks fine.

   ```bash
   cd /tmp && python3 -c "import tiny_mq; print('OK')"
   ```

5. **Check the annotation namespace.** Runtime-evaluated annotations need
   every name they mention to be imported. `typing.Callable`,
   `collections.abc.Callable`, `typing.Coroutine`,
   `collections.abc.Coroutine` are different imports and only some of
   them exist in every version you claim to support.

## The Sibling Defect From The Same Sweep

`tiny-callback`'s README used `.finally(cleanup)` in four places.
`finally` is a **reserved keyword** — it cannot be a method name; the
method is `finally_fn`, and the library's own docstring said so while its
README contradicted it. The whole example was a `SyntaxError`.

The README also had `lambda (users, products, orders): ...` — Python has no
tuple lambda parameters.

`tiny-watch`'s README had `from tiny_watch import watch, ignore, debounce`.
There is no `debounce` symbol; debouncing is the `debounce_ms` argument to
`watch()`. **The library was fine; the README was not.**

**Rule: every python block in a README must compile**, and every name a
library README imports must exist:

```python
BLOCK = re.compile(r"```python\n(.*?)```", re.S)
for block in BLOCK.findall(text):
    compile(block, "README.md", "exec")
```

```python
missing = {n for n in imported if not hasattr(module, n)}
assert not missing
```

See also `prompts/readme-claims-must-be-runnable.md` and
`prompts/python-support-is-a-claim.md` (an annotation is a runtime claim
about the Python version).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
