# CI design and release notes

## Goals

1. **PR runner fidelity** — changes in this repo are what benchmark *envs* execute (`ASV_RUNNER_PATH`).
2. **Upstream guard** — `airspeed-velocity/asv` on `main` must still work with the **published** `asv-runner` pin (catch asv×PyPI skew).
3. **Optional deep suite** — `/trigger-asv` runs asv's full `triggered.yml` (slow; needs secrets + healthy asv workflow).

## `test_asv` matrix (required on every PR)

| `runner_source` | Host `pip` | `ASV_RUNNER_PATH` in pytest | Protects against |
|-----------------|------------|-----------------------------|------------------|
| `pr` | asv[test] + editable this repo | `../asv_runner` (relative; see below) | Regressions in the PR |
| `pypi` | asv[test] only | *unset* | Broken **asv main × PyPI runner** |

Focused modules: `test_benchmarks`, `test_runner`, `test_console`, `test_statistics` (high signal for runner contracts without full Chrome matrix).

### Why a relative `ASV_RUNNER_PATH`?

asv's `ParsedPipDeclaration` only accepts a **single** absolute path segment (`/\w+/`). Multi-segment paths such as `/home/runner/work/...` become `/home/` and `pip install` fails. Track **asv-8650**; until fixed, always use a relative path from the asv checkout (e.g. `../asv_runner` or `./latest_asv_runner`).

## Other PR checks

| Workflow | Purpose |
|----------|---------|
| **prek** | Lint/format + **check-added-large-files --maxkb=1000** |
| **unit-tests** | `unittest discover` (smoke imports + py3.7 AST gate) |
| **Documentation** | Sphinx HTML artifact `documentation` |
| **Comment docs download on PR** | Sticky PR comment with nightly.link zip |
| **Links (lychee)** | Markdown / docs sources (non-blocking excludes in `lychee.toml`) |
| **Build wheels** | sdist/wheel build (publish only on `v*` tags) |

## `/trigger-asv`

1. Comment `/trigger-asv` on the asv_runner PR.
2. `slashdot_trigger.yml` → `repository_dispatch` `trigger-asv-command`.
3. `trigger_asv.yml` dispatches **asv** `triggered.yml` on **`main`** with `pr_number`.
4. asv should checkout `refs/pull/<n>/head` and set **`ASV_RUNNER_PATH`** (not `ASV_RUNNER`) to a **relative** path; ideally run **pr** and **pypi** legs (see HaoZeke/asv branch `fix/triggered-asv-runner-path`).

## Release (after feature PRs on main)

```bash
tbump 0.2.2 --dry-run && tbump 0.2.2
git push origin main --tags   # build_wheels → PyPI on v*
```

Prefer `prek run -a` locally (see `prek.toml`). Use `PDM_BUILD_SCM_VERSION` if editable installs hit dirty SCM wheel names.


## `/trigger-asv` operations checklist

Slash-command workflows always run from the **default branch** (`main`), not the PR head. So `trigger_asv.yml` / `slashdot_trigger.yml` fixes in this PR apply only **after #24 is merged**.

1. Rotate/recreate **`ASV_TOK`** on `airspeed-velocity/asv_runner` (classic PAT or fine-grained) with:
   - `repo` on asv_runner (reactions, contents)
   - `actions: write` / workflow dispatch on **airspeed-velocity/asv**
2. Merge this PR so `ref: main` (not `master`) is what `main` dispatches.
3. Merge asv PR updating `triggered.yml` (`ASV_RUNNER_PATH`, dual pr/pypi) — branch `HaoZeke/asv:fix/triggered-asv-runner-path`.
4. Comment `/trigger-asv` again; expect **Trigger asv** + asv **Triggered** success.

Until then, **required protection is the `test_asv` matrix (pr + pypi)** on every PR — not the slash command.
