# Local Markdown Format

## Write

Use the `Write` tool:

- **Request path**: `{reviews_dir}/{session}-request.md`
- **Content**: per `../schema.md`

## Success / Failure

Success: `Write` returns without error. This format essentially never fails.
Failure: `Write` error (disk full, permissions).

## Reviewer Prompt Template

```
Review requested — topic: {session-slug}.

Do not reply here. Use the Write tool to write a file.

1. Read: {reviews_dir}/{session}-request.md
2. Write your findings to: {reviews_dir}/{session}-response.md

Both paths are absolute. Do not use your current working directory.
```

## Response Location

`{reviews_dir}/{session}-response.md` — read with the `Read` tool.

## Cleanup

```bash
test -f {reviews_dir}/{session}-request.md && rm {reviews_dir}/{session}-request.md
test -f {reviews_dir}/{session}-response.md && rm {reviews_dir}/{session}-response.md
```
