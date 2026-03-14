---
name: logseq-db-query
description: >
  Use this skill to query a Logseq DB graph from the command line — especially
  when the Logseq app is closed, MCP tools are unavailable, or you need a
  complex cross-entity DataScript query that MCP tools can't express (e.g.
  filtering by tag AND date range, full-text search with conditions, bulk
  export). Trigger on: "app is closed, find X in my logseq graph", "without
  opening logseq, show me...", "find all #Task blocks from last week", "query
  my graph for blocks matching X and Y", "export my logseq graph", or any
  read/search request where MCP tools are insufficient or unavailable. Prefer
  MCP tools (listPages, searchBlocks, etc.) when the app is open and the query
  is simple. Use this skill for complex queries or offline access. Do NOT use
  for writes — use MCP upsertNodes instead.
---

# Logseq DB Query Skill

Query a Logseq DB graph directly from SQLite — no app, no MCP, no HTTP API required.

## When to use this vs MCP tools

| Situation | Use |
|-----------|-----|
| App is open, simple lookup (list pages, get a page) | MCP tools |
| App is closed / MCP unavailable | This skill (CLI) |
| Complex filter: tag + date range, multi-entity join | This skill (CLI) |
| Full-text search across block content | This skill (`search` or `block-content` rule) |
| Write operations | MCP `upsertNodes` only |

The CLI reads SQLite directly, so it only sees data the app has flushed to disk. If the app is open and you just wrote something, MCP tools will see it; CLI may not.

## Prerequisites

- [@logseq/cli](https://www.npmjs.com/package/@logseq/cli) installed: `npm install -g @logseq/cli`
- A Logseq DB graph (not file-based/markdown)
- Binary is typically at `~/.npm-global/bin/logseq`

---

## Discover Graphs

```sh
logseq list           # all local graph names
logseq show GRAPH     # metadata: path, schema version, created date
```

Graphs live in `~/logseq/graphs/` by default. Use the short name (e.g. `agents`), not the full path.

---

## Query Command

```sh
logseq query 'DATALOG' -g GRAPH
logseq query 'DATALOG' -g GRAPH -p   # expand entity refs to readable values
```

### CRITICAL: Argument Order

The query string **must come before** `-g`. Otherwise `-g` treats it as a second graph name and returns empty results:

```sh
# correct
logseq query '[:find ...]' -g agents

# wrong - query string consumed as graph name
logseq query -g agents '[:find ...]'
```

### DataScript Notes

- CLI automatically adds `:in $ %` (rules) — do NOT include `:in` yourself
- Built-in rules include `block-content` for full-text matching (see below)
- Common attributes: `:block/title`, `:block/uuid`, `:block/journal-day`, `:block/page`, `:block/parent`, `:block/order`, `:block/tags`
- Journal dates are integers: `YYYYMMDD` (e.g. `20260310`)

---

## Common Query Patterns

**Journal page by date:**
```sh
logseq query '[:find (pull ?p [:block/title :block/uuid]) :where [?p :block/journal-day 20260310]]' -g agents
```

**Blocks on a journal page:**
```sh
logseq query '[:find (pull ?b [:block/title :block/order]) :where [?b :block/page ?p] [?p :block/journal-day 20260310]]' -g agents
```

**All journal pages:**
```sh
logseq query '[:find (pull ?p [:block/title :block/journal-day]) :where [?p :block/journal-day _]]' -g agents
```

**Blocks on a named page:**
```sh
logseq query '[:find (pull ?b [:block/title]) :where [?b :block/page ?p] [?p :block/title "My Page"]]' -g agents
```

**All blocks with a tag:**
```sh
logseq query '[:find (pull ?b [:block/title :block/uuid]) :where [?b :block/tags ?t] [?t :block/title "Task"]]' -g agents
```

**Blocks with a tag on journal pages in date range** (complex — this is the DataScript sweet spot):
```sh
logseq query '[:find (pull ?b [:block/title]) :where [?b :block/tags ?t] [?t :block/title "Task"] [?b :block/page ?p] [?p :block/journal-day ?d] [(> ?d 20260303)]]' -g agents
```

**Full-text search using `block-content` rule:**
```sh
logseq query '[:find (pull ?b [:block/title :block/uuid]) :where (block-content ?b "nix")]' -g agents
```

**All pages with a tag:**
```sh
logseq query '[:find (pull ?p [:block/title :block/uuid]) :where [?p :block/tags ?t] [?t :block/title "genesis"]]' -g agents
```

**All tags (classes):**
```sh
logseq query '[:find (pull ?t [:block/title :block/uuid]) :where [?t :block/tags :logseq.class/Tag]]' -g agents
```

**Entity lookup by UUID:**
```sh
logseq query '69adf5c2-a62b-42b0-b3e0-5906f37d3f10' -g agents
```

**With readable property values:**
```sh
logseq query '[:find (pull ?b [*]) :where [?b :block/page ?p] [?p :block/title "My Page"]]' -g agents -p
```

---

## Search Command

Fast keyword search across `:block/title` content. Good for quick lookups when you don't need filters.

```sh
logseq search 'meeting notes' -g agents
logseq search 'meeting notes' -g agents -l 20   # limit results (default 100)
logseq search 'meeting notes' -g agents -r       # raw output
```

For full-text search with additional filters (e.g. only on journal pages), use `query` with the `block-content` rule instead.

---

## Bulk Export

```sh
logseq export-edn -g agents > graph.edn     # full graph as EDN (DataScript format)
logseq export -g agents > graph.json        # full graph as JSON
```

Useful for offline analysis, backups, or feeding the graph into other tools.

---

## Known Issues

- CLI only sees data flushed to SQLite — if app is open, very recent writes may not appear
- `search` only searches `:block/title`, not nested properties (use `block-content` rule in `query` for deeper search)
