# Request Schema

The canonical shape of a peer-review request. All formats encode these fields — exact serialization varies per format file.

## YAML Front Matter

```yaml
agent: string        # harness name: "Claude Code", "opencode", "kiro" — NOT the model ID
model: string        # model ID, e.g. "claude-sonnet-4-6"
working_dir: string  # absolute path of the current working directory
timestamp: string    # UTC ISO 8601 — output of: date -u +%Y-%m-%dT%H:%M:%SZ
prompt: |            # verbatim text of the user message that triggered this review
  string
focus?: string       # the specific question from the `question` parameter
```

`focus` is optional — omit the field entirely if no question was provided. Do not set it to an empty string.

## Body

```
## What to do

{1–2 sentences: what is being reviewed, what kind of review,
and where to write the response. Include the absolute response path so the reviewer can
re-orient from the file alone if the tmux message is lost.}

## Context

{Everything the reviewer needs:
 - file path(s) or code snippets under review
 - relevant background or motivation
 - any pre-analysis or findings you want to share
 - the specific question if focus was set}
```
