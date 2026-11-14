# Static Toolchain Install Without Root, apt, `xz`, or `unzip`

**Last verified:** 2026-11-14 — every command below was run on this container.
What was reproduced **this** session, first-hand:

| run | result |
|---|---|
| NullMotion `node --test`, `TMPDIR=/home/node/.cache/tmp-exec` | **27 / 27 pass** |
| same, `TMPDIR=/tmp` (512 MB tmpfs) | **25 pass, 2 fail** — `extractAudio` cache + reference-audio route |
| MotionClone `pytest`, as shipped | **2 failed, 125 passed, 1 skipped** |
| + `hyperframes/npm ci`, `channel='chrome'` → `executable_path` | **3 failed, 125 passed** (new: `test_hyperframes`) |
| + `HYPERFRAMES_BROWSER_PATH=<chromium>` | **128 passed** |

Host facts re-checked: `/tmp` is `tmpfs … noexec,size=524288k`; a binary
written to `/home/node/.cache/tmp-exec` executes (`ok`);
`chrome-157/chrome-linux64/chrome --version` → **Google Chrome for Testing
157.0.8103.78**, `chromium-1208` → **145.0.7632.6**. *(Superseded claim: an
earlier edit of this file said "NullMotion 2 fail → 0, MotionClone 15 fail →
0". Those counts were never reproduced — the measured numbers are above.)*

## When to use this

A test suite or build fails with `FileNotFoundError`, `EACCES`, or
`switching to root user to install dependencies` and the missing piece is a
**binary**, not a package: `ffmpeg`, `ffprobe`, a browser, `zig`, a static
Go toolchain.

Constraints on this host, all verified:

| constraint | check | value |
|---|---|---|
| no root, no sudo | `id -u`, `command -v sudo` | no sudo, `CapEff: 0000000000000000` |
| no user namespaces | `unshare -r true` | `Operation not permitted` |
| no apt | `apt-get update` | `/var/lib/apt/lists/partial is missing` |
| no `xz` | `command -v xz unzip` | both missing |
| `/tmp` is `noexec` | `mount \| grep ' /tmp '` | `nosuid,nodev,noexec` |
| `/tmp` is 512 MB | `df -h /tmp` | tmpfs, 512M |

**Everything installs under `/home/node/`.** Nothing installs to `/opt`.

## The extraction rule

There is no `xz` and no `unzip`. Shell out to Python — stdlib only:

```bash
# .tar.xz  (ffmpeg static builds, zig, Go)
python3 - <<'PY'
import lzma, tarfile
tarfile.open("/home/node/dl/ffmpeg.tar.xz", "r:xz").extractall("/home/node/dl/ffmpeg")
PY

# .zip  (Chrome for Testing, some tooling)
python3 -m zipfile -e /home/node/dl/chrome.zip /home/node/dl/chrome
# or: python3 -c "import zipfile; zipfile.ZipFile('...').extractall('...')"
```

`tar xf file.tar.xz` fails with `Child returned status 2`, which reads like a
corrupt download. It is a missing decompressor.

## ffmpeg / ffprobe

```bash
mkdir -p /home/node/.local/bin /home/node/dl
curl -fsSL https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
  -o /home/node/dl/ffmpeg.tar.xz
python3 -c "import tarfile; tarfile.open('/home/node/dl/ffmpeg.tar.xz').extractall('/home/node/dl/ff')"
d=$(find /home/node/dl/ff -maxdepth 1 -name 'ffmpeg-*-static' | head -1)
cp "$d/ffmpeg" "$d/ffprobe" /home/node/.local/bin/
/home/node/.local/bin/ffmpeg -version | head -1
```

## Chrome for Testing (when a suite hardcodes `channel='chrome'`)

```bash
V=157.0.8103.78
curl -fsSL "https://storage.googleapis.com/chrome-for-testing-public/$V/linux64/chrome-linux64.zip" \
  -o /home/node/dl/chrome.zip
python3 -m zipfile -e /home/node/dl/chrome.zip /home/node/.cache/ms-playwright/chrome-157
/home/node/.cache/ms-playwright/chrome-157/chrome-linux64/chrome --version
```

Two binaries exist on this host and **both report the same product**, so
checking the version string tells you nothing about which one a suite used:
`chrome-157` → 157.0.8103.78, `chromium-1208` → 145.0.7632.6.

Then point the channel at a path from a pytest fixture rather than editing
the test. The monkeypatch target is the class, not a function:

```python
@pytest.fixture(autouse=True)
def _chrome_path(monkeypatch):
    real = playwright.sync_api.BrowserType.launch
    def _launch(self, **kw):
        kw.pop("channel", None)
        kw["executable_path"] = os.environ["CHROME_PATH"]
        return real(self, **kw)
    monkeypatch.setattr(playwright.sync_api.BrowserType, "launch", _launch)
```

The one-off version, used here to prove the diagnosis: `sed -i
"s/channel='chrome'/executable_path=os.environ.get('CHROME_PATH','')/"
app/scene_pipeline.py`, run the single test file, then `git checkout` it.
**A green run under a patched environment is a diagnosis, not a fix** — the
repo's own suite must still show its original failures when you revert.

HyperFrames needs the same binary via `HYPERFRAMES_BROWSER_PATH`. Its own
downloader fails here with *"no zip archiver is available. Install `unzip`"*
— read from `hyperframes-check.log`, not guessed: it wants
`chrome-headless-shell 152.0.7977.30` and cannot unpack the zip. The error
text names the two fixes that work (`HYPERFRAMES_BROWSER_PATH`, or the
`hyperframes` Docker image); setting one binary env var fixed that test and
took the suite from 3 failed to **128 passed**.

**A missing `node_modules` makes a suite redder, not greener.** `app/hyperframes.py:38`
copies `node_modules/gsap/dist/gsap.min.js`; with it absent the test dies on
`FileNotFoundError`, and after `npm ci` (`hyperframes/package.json`: `gsap`,
`hyperframes`) it reaches the renderer and fails on the browser instead — the
failure count goes **2 → 3**. Count install steps before the
first number, or the second number describes a different machine. `npm ci`
also warned that `esbuild`, `onnxruntime-node`, `protobufjs` postinstalls
were **blocked** (npm 11 install-script policy) — silent here, fatal in a
bundler.

## Persist, do not re-derive

Append to `~/.profile` so every later run starts with a working environment:

```bash
export PATH="/home/node/.local/bin:$PATH"
export TMPDIR=/home/node/.cache/tmp-exec       # overlay, executable
export HYPERFRAMES_BROWSER_PATH=/home/node/.cache/ms-playwright/chrome-157/chrome-linux64/chrome
```

`TMPDIR` must point at a path that can **execute** binaries, not just hold
them. `/home/node/.cache/tmp-exec` exists for exactly this; `mkdir -p` it and
`chmod 700`.

## The three-diagnosis shape

The same suite needed all three fixes, and each masked the next. Fix them in
this order and re-run after each — a single "it still fails" after all three
tells you nothing.

| # | symptom | real cause | check |
|---|---|---|---|
| 1 | assertion `false !== true` | helper binary in `noexec` tmpdir | `mount \| grep /tmp` |
| 2 | `su: Authentication failure` | `channel='chrome'` + root-owned `/opt` | `ls -ld /opt` |
| 3 | bundler missing at build | npm 11 blocked install scripts | `npm install-scripts approve <pkg>` |

## Verify with the tool, not the install log

```bash
ffmpeg -version | head -1
ffprobe -version | head -1
node -e 'require("esbuild").transformSync("let a=1"); console.log("esbuild OK")'
```

An install that printed `OK` and a binary that runs are different claims.
See `tools/uv-venv-toolchain-guide.md` for the Python side and
`skills/dev-env-defects/` for the triage order.
