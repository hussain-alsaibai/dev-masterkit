# Valid YAML Is Not A Valid Workflow

**A rule for every generator, template, or script that writes a GitHub
Actions workflow.**

> Found 2026-11-04. Three CI workflows passed `yaml.safe_load` and still
> failed every matrix job:
>
> ```
> [error]The version '${ matrix.python-version }' with architecture 'x64'
>         was not found for Ubuntu 24.04.
> ```
>
> The template was built with Python `str.format()`, and `{{` collapsed to
> `{`. The file written was `${ matrix.python-version }` — **one brace
> short** — so `setup-python` received the literal string instead of the
> matrix expression.
> **Last verified:** 2026-11-04 — reproduced by writing the same
> `str.format()` template and parsing it; the parsed value was
> `'${ matrix.python-version }'` where the workflow required
> `'${{ matrix.python-version }}'`.

## The Rule

> **Assert on the parsed VALUE, not on the fact that parsing succeeded.**

`yaml.safe_load` was perfectly happy with `${ ... }`. **The YAML was never
wrong; the workflow was.** Parsing succeeds on a million documents that
mean nothing, because YAML is a data format and it will happily hold any
scalar you hand it.

## Why `str.format()` Is The Wrong Tool Here

GitHub Actions expressions are `${{ ... }}`. Python's `str.format()` uses
`{...}` for interpolation and `{{...}` for a literal brace. So:

| you write | after `str.format()` | what GitHub sees |
|---|---|---|
| `${{ matrix.python-version }}` | `${ matrix.python-version }` | a literal string |
| `${{ matrix.python-version }}` (escaped) | `${{ matrix.python-version }}` | the expression |

The bug is invisible because **both outputs are valid YAML** and **both
strings look plausible in a diff**.

## The Procedure

1. **Assert the parsed value**, not the parse:

   ```python
   doc = yaml.safe_load(body)
   assert doc["jobs"]["test"]["steps"][1]["with"]["python-version"] == \
       "${{ matrix.python-version }}"
   ```

2. **Build workflow YAML from a known-good file**, not from a hand-written
   template string. Copy a file that already works; do not re-derive the
   braces.

3. **If you must generate it, use `%`-formatting or `string.Template`, and
   never `str.format()`** on a body that contains `${{`.

   ```python
   # safe: no braces are interpolation syntax
   body = TEMPLATE % {"name": repo_name}
   # or
   body = Template(TEMPLATE).substitute(name=repo_name)
   ```

4. **Validate the whole workflow against the schema**, not just the one
   step you were fixing. See `skills/validate-workflow-schema` — it exists
   because six of our repos once carried `continue_on_error` instead of
   `continue-on-error`, and **one token** made GitHub reject the file so
   that **no job ran at all**.

5. **Diff the generated file against a hand-checked one** before pushing.
   A one-character diff in a workflow file is a one-character outage.

## The Lucky Part

The fifteen workflows written earlier from the same `str.format()` template
were checked afterwards and were all correct. **That was luck, not design.**
A template that silently eats a brace will eventually be used on a host
where the value differs.

## The Generalisation

Any generated configuration file has the same shape: the generator emits
text, and the consumer parses it. **Parsing is not validation.** Validate
the fields the consumer will actually use, by value.

See also `prompts/validate-workflow-schema.md`,
`prompts/spec-literal-must-be-generated.md` (generate the literal the
spec demands, then check it) and
`prompts/ci-target-must-match-repo-layout.md` (a workflow that parses and
runs nothing).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
