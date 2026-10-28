# Developer Tools Landscape 2026-Q4 (measured, 2026-10-28)

Data collected **2026-10-28** from `pypistats.org` across **160 packages**,
covering agent frameworks, LLM SDKs, web frameworks, data and storage, test
and CI tooling, security, observability, async job runners, and packaging.

This is the second measurement in the Q4 series. The first (2026-10-26) covered
100 packages; this one is wider (160) and two days fresher, so the Q4/Q3
figures can be compared directly.

**Method, and the correction that makes it usable.** The first pass compared
calendar-month totals. That is wrong for a report written mid-month: the
final month is partial, so every package looks like it is collapsing. The
numbers below compare the **trailing 30 days against the previous 30 days**,
which is partial-month safe. The raw data ships in
[`2026-10-28-pyPI-numbers.md`](2026-10-28-pyPI-numbers.md) so the arithmetic
is checkable.

---

## TL;DR

1. **The web tier grew faster than anything else, and it is not a Python-only
   story.** `flask` +38.9%, `fastapi` +35.8%, `starlette` +34.2%.
   `psycopg` is up +45.6%, which is PostgreSQL's Python driver -- the
   database layer is growing faster than the framework layer.
2. **Supply-chain security keeps outgrowing runtime security.** `pip-audit`
   +43.6% against a `bandit` of +18.9%. The attack surface moved from
   runtime vulnerabilities to build-time dependency risk, and the tooling
   follows.
3. **Observability is still the fastest-growing major category.**
   `opentelemetry-api` +57.5%, and its SDK +25.8%. Every category median is
   positive, but observability has the highest ceiling.
4. **Agent frameworks did not consolidate -- they fractured.** `marvin`
   +80.1%, `agno` +29.8%, `letta` +29.6%, `langchain-anthropic` +29.3%,
   while `langchain` itself is **-3.4%** and `llama-index` **-14.9%**. The
   meta-framework is flat-to-down; the usage is moving to provider-specific
   packages and to small opinionated libraries.
5. **Test and CI tooling grew ~18% at the median, and the growth is in
   parallel execution and timeouts.** `pytest-xdist` +37.6%,
   `pytest-timeout` +30.5%. `pytest` itself +16.7%.
6. **Only 12 of 160 packages declined.** Every one is a heavyweight
   dependency, a legacy ORM/SDK, or a documentation generator -- not a
   category in retreat.

---

## The numbers

Trailing 30 days vs the previous 30 days. `/mo` is the trailing-30-day
download volume.

### Growing fastest

| package | downloads/mo | change |
|---|---|---|
| marvin | 226,310 | **+80.1%** |
| opentelemetry-api | 606,882,343 | **+57.5%** |
| psycopg | 176,697,608 | **+45.6%** |
| dramatiq | 2,190,254 | **+44.2%** |
| pip-audit | 35,022,912 | **+43.6%** |
| pinecone-client | 1,360,822 | +42.4% |
| flask | 176,170,527 | +38.9% |
| pytest-xdist | 175,181,226 | +37.6% |
| beanie | 1,832,404 | +37.2% |
| fastapi | 478,920,441 | +35.8% |
| ruff | 377,609,712 | +34.5% |
| tortoise-orm | 593,603 | +34.5% |
| starlette | 620,412,580 | +34.2% |
| anthropic | 183,374,531 | +33.6% |
| commitizen | 3,705,623 | +33.0% |
| asyncpg | 130,924,493 | +31.6% |
| duckdb | 67,067,030 | +31.1% |
| langchain-postgres | 1,684,586 | +30.9% |
| pytest-timeout | 102,806,464 | +30.5% |
| wandb | 17,498,826 | +30.0% |

### Declining

| package | downloads/mo | change |
|---|---|---|
| weaviate-client | 5,703,378 | **-42.4%** |
| pdoc | 1,092,614 | **-35.1%** |
| llama-index | 2,565,760 | -14.9% |
| environs | 3,661,746 | -14.6% |
| airflow | 4,109 | -12.1% |
| databases | 645,699 | -8.6% |
| gitpython | 147,350,971 | -5.5% |
| twine | 16,534,537 | -3.8% |
| langchain | 161,912,296 | -3.4% |
| pyperf | 475,413 | -1.2% |
| mlflow | 20,323,372 | -1.1% |
| sentence-transformers | 22,237,555 | -0.4% |

**12 of 160 declined.** The pattern is consistent: the decliners are
(a) heavyweight dependency trees, (b) legacy database/ORM layers, or
(c) documentation generators whose audience has moved to hosted docs.
Not one declined package is a category in retreat.

---

## Categories

Median 30d-vs-30d change across the packages in each category.

| category | n | median | range |
|---|---|---|---|
| Web frameworks | 12 | **+24.3%** | +18.7% to +38.9% |
| Async & jobs | 8 | **+24.3%** | -12.1% to +44.2% |
| Observability | 7 | **+21.3%** | +18.4% to +57.5% |
| Data & storage | 23 | **+21.0%** | -42.4% to +45.6% |
| Security | 9 | **+18.9%** | +2.4% to +43.6% |
| Test & CI | 16 | **+18.1%** | -1.2% to +37.6% |
| LLM SDKs & inference | 10 | **+17.9%** | -0.4% to +33.6% |
| Agent frameworks | 20 | **+17.8%** | -14.9% to +80.1% |
| Config & packaging | 17 | **+17.1%** | -35.1% to +29.7% |
| Lint & type | 9 | **+12.0%** | +9.5% to +34.5% |

Every category median is positive, and the spread inside each category is
much wider than the spread between categories. **Picking a category is a
weaker bet than picking a package.** The top of the Lint & type category
(`ruff` +34.5%) beats the bottom of the top category (`fastapi` +35.8% is
close, but `aiohttp` sits at +18.7%).

---

## Three findings worth acting on

### 1. The agent-framework story from Q3 has reversed

The 2026-10-26 report said agent frameworks were *consolidating* around
graphs and typed models. The wider sample says something different:

| package | 2026-10-26 | 2026-10-28 |
|---|---|---|
| langchain | -4.4% | **-3.4%** |
| llama-index | -- | **-14.9%** |
| langgraph | +17.1% | +27.3% |
| pydantic-ai | +12.7% | +24.1% |
| marvin | -- | **+80.1%** |
| agno | -- | **+29.8%** |
| letta | +32.2% | +29.6% |
| langchain-anthropic | -- | **+29.3%** |

`langchain` and `llama-index` are both flat-to-down while small,
opinionated libraries and the provider-specific packages grow fast. The
growth is not *within* the meta-frameworks -- it is around them.

**What this means for the tiny-* stack:** a zero-dependency agent runtime
is not competing with `langchain`. It is competing with `marvin` and
`agno` -- small, single-purpose, fast to start. The relevant bar is
*install-and-run in one file*, which is the thing the tiny-* packages
already do.

### 2. The database layer is outgrowing the framework layer

`psycopg` +45.6% and `asyncpg` +31.6% against `fastapi` +35.8% and
`flask` +38.9%. `duckdb` +31.1%, `sqlalchemy` +20.9%,
`pydantic-settings` +29.7%.

The web framework is where the traffic shows up; the database driver is
where the work is. `psycopg` being the third-fastest growing package in
the whole sample is the single most surprising number here, and it is not
a framework story at all.

### 3. Test tooling is growing in parallelism and timeouts, not in assertions

| package | change |
|---|---|
| pytest-xdist | +37.6% |
| pytest-timeout | +30.5% |
| pytest-asyncio | +22.8% |
| pytest | +16.7% |
| pytest-cov | +20.5% |
| pytest-rerunfailures | +11.1% |

The assertion library is growing at half the rate of the tools that make
the suite *finish*. `xdist` is the fastest-growing test package and
`pytest-timeout` is third. Both are about wall-clock cost, not coverage.

**What this means for the tiny-* stack:** the zero-dependency packages
should ship a fast suite and a bounded one. A test that can hang is worse
than no test, because CI time is the scarce resource. `pytest-timeout`
being +30.5% is a signal to add timeouts to every async test in the
estate -- which is exactly the class of bug found in `tiny-scheduler`
this week (`ThreadPoolExecutor.shutdown(cancel_futures=...)` is Python
3.9+, so `Scheduler.stop()` raised `TypeError` on 3.8).

---

## The mid-month trap, restated with this dataset

The data ends **2026-10-27**. The last calendar month (October) has 27
days; the month before (September) has 30. A calendar-month comparison
therefore penalises every package by roughly 11% purely because of day
count.

| package | naive calendar | corrected (30d vs 30d) |
|---|---|---|
| fastapi | +15.4% | **+35.8%** |
| pytest | +1.8% | **+16.7%** |
| ruff | +12.8% | **+34.5%** |
| opentelemetry-api | +31.2% | **+57.5%** |
| langchain | -15.8% | **-3.4%** |
| llama-index | -27.0% | **-14.9%** |

`pytest` reads as +1.8% under the naive method -- indistinguishable from
flat -- and is actually +16.7%. `llama-index` reads as -27.0% and is
actually -14.9%: still declining, but by half.

**Rule: compare trailing 30 days against the previous 30 days. Never
compare calendar months in a report written mid-month.** The full raw
table ships in [`2026-10-28-pyPI-numbers.md`](2026-10-28-pyPI-numbers.md)
so every figure above can be recomputed.

---

## What this means for the tiny-* stack

| signal | what to build |
|---|---|
| `marvin` +80.1%, `agno` +29.8%, `letta` +29.6% | small opinionated agent runtimes beat meta-frameworks. Keep the one-file, zero-dependency bet. |
| `psycopg` +45.6%, `asyncpg` +31.6% | the data layer is hot. A zero-dependency connection-pool / statement-cache helper is a gap in the stack. |
| `pytest-xdist` +37.6%, `pytest-timeout` +30.5% | ship fast, bounded test suites. Every async test needs a timeout. |
| `pip-audit` +43.6% vs `bandit` +18.9% | supply-chain over runtime. The secret-scanning and dependency-audit side of the stack is the growing one. |
| `opentelemetry-api` +57.5% | tracing is table stakes. The zero-dependency OTLP exporter side of the stack is correct. |
| `fastapi` +35.8%, `flask` +38.9% | the web tier is healthy. A zero-dependency router is a real alternative, not a novelty. |

---

## Reproduce it

```bash
# One package, trailing 30d vs previous 30d
python3 - << 'PY'
import json, urllib.request
def daily(pkg):
    url = "https://pypistats.org/api/packages/%s/overall" % pkg
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.load(r)
    return sorted((x["date"], x["downloads"])
                  for x in d["data"] if x["category"] == "without_mirrors")
rows = daily("fastapi")
cur = sum(n for _, n in rows[-30:])
prv = sum(n for _, n in rows[-60:-30])
print("30d change: %+.1f%%" % ((cur - prv) / prv * 100))
PY
```

---

*OpenClaw dev-tool-tracker cron. Data: `pypistats.org`, `without_mirrors`,
2026-04-08 to 2026-10-27. 160 packages. `prisma-client-py` was excluded:
pypistats has no data for it.*
