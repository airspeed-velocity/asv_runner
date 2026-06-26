# CI and release notes (asv_runner)

## PR CI (dual asv guard)

Workflow **test_asv** runs focused asv tests twice per Python version:

1. **pr** — `ASV_RUNNER_PATH=../asv_runner` so benchmark envs install this PR's runner (path must be relative until asv fixes multi-segment absolutes).
2. **pypi** — no `ASV_RUNNER_PATH`; envs use asv's declared `asv-runner` pin (catches broken **upstream asv × published runner**).

## `/trigger-asv`

Comment `/trigger-asv` on an asv_runner PR (requires `ASV_TOK`). Dispatches asv **`triggered.yml` on `main`** with the PR number so asv checks out `refs/pull/<n>/head`. That workflow must use **`ASV_RUNNER_PATH`** (not `ASV_RUNNER`) and a path form asv can install — track vault issue **asv-8650** and an asv PR for `triggered.yml` if slash-command full suite still mis-installs the PR runner.

## Release

Use `tbump` on main after feature PRs land; tag `v*` publishes via `build_wheels.yml`.
