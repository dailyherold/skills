# Logseq Format

## Write

Use `mcp__logseq-db__upsertNodes` to create a page and a single block containing the full request content (per `../schema.md` — front matter + body as a single markdown string).

```json
{
  "operations": [
    {
      "operation": "add",
      "entityType": "page",
      "id": "temp-pr-request",
      "data": { "title": "peer-review/{session}" }
    },
    {
      "operation": "add",
      "entityType": "block",
      "data": {
        "page-id": "temp-pr-request",
        "title": "{full request content as a single string}"
      }
    }
  ]
}
```

## Success / Failure

Success: `upsertNodes` returns without error.
Failure: MCP tool throws or errors (Logseq app closed, MCP server not running).

## Reviewer Prompt Template

```
Review requested — topic: {session-slug}.

Do not reply here. Write your findings to Logseq.

1. Read: use mcp__logseq-db__getPage with pageName "peer-review/{session}"
2. Write your findings: use mcp__logseq-db__upsertNodes to create page "peer-review/{session}-response"
```

## Response Location

Logseq page `peer-review/{session}-response` — read with `mcp__logseq-db__getPage` → `pageName: "peer-review/{session}-response"`.

## Cleanup

Pages are low-cost in Logseq — leave them or delete manually in the app.
