# Check npm Name Ownership Before Telling Users to Install

**A name on npm is not yours because you want it.**

> Found 2026-10-25: the `context-bridge` README told users to run
> `npm install -g context-bridge`. That command installs **someone else's**
> package — npm `context-bridge` is owned by `memo-cn` (i@memo.cool), an
> unrelated Electron/JS inter-context bridge, last published 2023-12-17.
> We had never published to npm at all. **Last verified:** 2026-10-25 —
> registry lookup of `context-bridge`, and the scope availability checks
> below.

## The Rule

> **Before a README, guide, or chat message tells anyone to install a package,
> verify who owns that name on the registry.** It takes one request.

```bash
curl -s https://registry.npmjs.org/context-bridge | python3 -c '
import sys, json
d = json.load(sys.stdin)
print("name:   ", d.get("name"))
print("owner:  ", d.get("maintainers"))
print("latest: ", d.get("dist-tags", {}).get("latest"))
print("repo:   ", d.get("repository"))
print("desc:   ", (d.get("description") or "")[:100])
'
```

For `context-bridge` that returns:

```
name:    context-bridge
owner:   [{'name': 'memo-cn', 'email': 'i@memo.cool'}]
latest:  1.0.0
repo:    git+https://github.com/memo-cn/context-bridge.git
desc:    Electron/JS inter-context bridge
```

None of that is our project. The install line in our README would have
installed a 2023 Electron package for anyone who followed it.

## Why It Is Easy To Get Wrong

- The name matches **our** project name, because we named our project after
  our own product. The registry has no idea who we are.
- The install line was written when the package did not exist yet, or was
  copied from another project's README.
- A **scoped** name is not automatically free either: scopes can be claimed
  by anyone, and the ownership rules are not obvious.

## Choosing a Name That Is Actually Free

Check the scope and the alternatives before committing to one:

```bash
# does the scope exist, and is it ours?
curl -s -o /dev/null -w '%{http_code}\n' https://registry.npmjs.org/@alsaibai
# 404 = scope does not exist (fine to create, if the name is free)
# 200 = scope exists (check who owns it)

# is the scope registered to us?
npm owner ls @alsaibai 2>&1 | head

# candidate names
for n in context-bridge-mcp context-bridge-mcp-server contextbridge \
         @alsaibai/context-bridge @hussain-alsaibai/context-bridge; do
  code=$(curl -s -o /dev/null -w '%{http_code}' https://registry.npmjs.org/$n)
  echo "$n -> $code"
done
```

Measured on 2026-10-25:

| Candidate | Result | Verdict |
|-----------|--------|---------|
| `context-bridge` | taken by `memo-cn` | **do not use** |
| `context-bridge-mcp` | taken by `kamlesh62` | do not use |
| `@alsaibai/context-bridge` | scope exists, package free | **recommended** |
| `@hussain-alsaibai/context-bridge` | scope does not exist | acceptable fallback |
| `context-bridge-mcp-server` | free | generic, avoid |
| `contextbridge` | free | generic, avoid |

**A scope that 404s does not mean it is unavailable** — it means it has never
been created. A scope that 200s might belong to someone else.

## The Interim Fix (While Publishing Is Blocked)

Until the package is actually on the registry under a name we own, do not
tell users to install a name that means something else:

```bash
# BAD - installs someone else's package
git clone https://github.com/hussain-alsaibai/context-bridge.git
cd context-bridge && npm install
```

Put the clone+install path in the README, with a note explaining why. A
package that is not published under a name you own is not installable by
name, and the install line is the single most-copied line in a README.

## The Verification Discipline

The registry check belongs in CI for a package you *do* publish:

```bash
# does the name still point at our repo?
curl -s https://registry.npmjs.org/$(npm pkg get name | tr -d '"') \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("repository"))'
# must print our repo URL, not someone else's
```

A rename or a transfer can change what a name points at. Check it in CI and
you find out the day it happens.

## The Generalisation

> **Before publishing an instruction that names an external artifact, verify
> that the artifact is the one you mean.** Names are allocated by whoever got
> there first, and a README is a set of instructions for using a name — not a
> description of a package.

The same check applies to:

- Docker Hub image names (`docker.io/<user>/<image>`),
- PyPI project names,
- Homebrew taps,
- GitHub Actions (`owner/repo@ref` — a fork can shadow the name you meant),
- Chrome Web Store extension names.

See also `prompts/readme-claims-must-be-runnable.md` — the install line is a
snippet, and snippets must be runnable against the thing they name.
