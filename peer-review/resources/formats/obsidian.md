# Obsidian Format

<!-- Configure: set vault_dir to your Obsidian vault's peer-review folder -->
<!-- vault_dir: /path/to/vault -->

Set `{vault_dir}` = the path in the comment above before proceeding.

## Write

Use the `obsidian` cli if available, otherwise use the `Write` tool directly — Obsidian does not need to be running:

- **Request path**: `{vault_dir}/{session}-request.md`
- **Content**: per `../schema.md` — identical content to local-markdown, different destination

## Success / Failure

Success: writing request returns without error.
Failure: writing request returns an error (vault path inaccessible, permissions).

## Reviewer Prompt Template

```
Review requested — topic: {session-slug}.

Do not reply here. Use the Write tool to write a file.

1. Read: {vault_dir}/{session}-request.md
2. Write your findings to: {vault_dir}/{session}-response.md

Both paths are absolute. Do not use your current working directory.
```

## Response Location

`{vault_dir}/{session}-response.md` — read with the `Read` tool.

## Cleanup

```bash
test -f {vault_dir}/{session}-request.md && rm {vault_dir}/{session}-request.md
test -f {vault_dir}/{session}-response.md && rm {vault_dir}/{session}-response.md
```
