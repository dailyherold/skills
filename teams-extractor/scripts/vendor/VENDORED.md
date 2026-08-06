# Vendored: ccl_simplesnappy

## Why

`teams_extractor.py` uses `ccl_chromium_reader` (pinned to a commit, via git
— see the script's PEP 723 header) as its LevelDB/IndexedDB parsing engine.
That library depends on `ccl_simplesnappy` for pure-Python Snappy
decompression, declared as an **unpinned** git URL (`@ HEAD`) in its own
`pyproject.toml`. Without vendoring, every `uv run` would resolve
`ccl_simplesnappy` to whatever is currently at `HEAD` — an unpinned,
unreviewed dependency — and require `git` solely to satisfy it.

`ccl_simplesnappy_pkg/` is a vendored copy of
[cclgroupltd/ccl_simplesnappy](https://github.com/cclgroupltd/ccl_simplesnappy),
pinned at commit `3d085230baa8c46cf2090ebba29bf6e8eab31087` (its only commit).
It's a single ~300-line pure-Python file with zero dependencies and no
compiled extensions (MIT-licensed, `LICENSE` included here), so vendoring it
carries low maintenance risk and keeps the dependency chain fully pinned and
auditable.

`git` is still required overall — `ccl_chromium_reader` itself isn't on PyPI
and must be fetched from GitHub. Vendoring removes only the second, unpinned
git dependency that would otherwise ride along with it.

## How it's wired in

`teams_extractor.py`'s PEP 723 header uses `[tool.uv.sources]` +
`[tool.uv] override-dependencies` to force `ccl_simplesnappy` to resolve from
`ccl_simplesnappy_pkg/` here instead of `ccl_chromium_reader`'s git URL. `uv`
resolves that relative path against the script's own directory, not the
caller's working directory, so it works regardless of where
`teams_extractor.py` is invoked from.

## Maintenance: when you bump the ccl_chromium_reader pin

Whenever you update the pinned `ccl_chromium_reader` commit, check whether
its `ccl_simplesnappy` dependency has changed at that new commit:

```bash
curl -s "https://raw.githubusercontent.com/cclgroupltd/ccl_chromium_reader/<new-commit>/pyproject.toml" | grep -A3 dependencies
```

If it still points at `ccl_simplesnappy @ git+https://github.com/cclgroupltd/ccl_simplesnappy.git`
with no rev pin, check whether that repo has moved past the vendored commit:

```bash
git ls-remote https://github.com/cclgroupltd/ccl_simplesnappy.git HEAD
```

If there's a newer commit, diff it against the vendored copy and re-vendor if
there's a real change worth pulling in. This is a small, low-churn library —
in practice this will rarely matter — but don't assume the pin here stays in
sync with upstream on its own.
