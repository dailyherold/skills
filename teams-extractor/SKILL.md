---
name: teams-extractor
description: >
  Read Microsoft Teams messages from the local Chromium IndexedDB cache — no
  API auth, no Entra app, no admin permissions required. Use this skill
  whenever the user wants to retrieve Teams messages, check what someone said
  in Teams, search Teams chat history, or capture a Teams message as a note.
  Trigger on: "check my Teams", "what did [person] say in Teams", "find
  [person]'s message about [topic] in Teams", "Teams DM from [person]", "capture that
  Teams message", or any request to read or search Teams chat history. Do NOT
  use for sending messages — read-only.
compatibility: Requires uv (for python-snappy) and Microsoft Teams running as the Chromium web app
license: MIT
---

# Teams Extractor

Reads Microsoft Teams messages directly from the local Chromium LevelDB cache.
No auth setup. No API calls. Works offline. Zero IT footprint.

## Available scripts

- **`scripts/teams_extractor.py`** — Extracts messages from a copied LevelDB
  cache. Supports filtering by sender display name, keyword search, and recency.
  Self-contained via PEP 723 inline deps — run with `uv run`.

## Prerequisites

- Teams must be open in Chromium (web app at `teams.cloud.microsoft`)
- `uv` must be available (`which uv`) — it handles `python-snappy` automatically

## Cache path

```
~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb/
```

> If Teams is used via the native app instead of Chromium, the cache path differs.
> Check `~/.config/` for other Teams-related IndexedDB directories.

## Step 1 — Copy the live cache

Teams holds a write lock on the LevelDB directory. Always copy first:

```bash
cp -r ~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb /tmp/teams_copy
```

## Step 2 — Run the extractor

### Get messages from a specific person

```bash
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --from-user 'Display Name Here' \
  --recent 20
```

### Search by keyword (all senders)

```bash
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --search 'keyword or phrase'
```

### Combine: messages from a person about a topic

```bash
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --from-user 'Jane Doe' \
  --search 'partnership' \
  --recent 10
```

### Extract your own sent messages (default mode)

```bash
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --recent 50
```

### Save to file

```bash
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --from-user 'Person Name' \
  --recent 30 \
  --output /tmp/teams_results.txt
cat /tmp/teams_results.txt
```

> For large result sets, always use `--output FILE` — output may be truncated
> if piped directly to the agent. Use `--recent N` to bound output size.

## Flags

```
uv run scripts/teams_extractor.py --help
```

| Flag | Description |
|------|-------------|
| `--from-user NAME` | Filter to messages FROM this display name. Disables sent-only filter. |
| `--search KEYWORD` | Filter to messages containing this string (case-insensitive). |
| `--recent N` | Return only the N most recent matching messages. |
| `--output FILE` | Write results to file instead of stdout. |

## Output format

One line per message:

```
[YYYY-MM-DDTHH:MM:SS] message text
```

Timestamps are UTC. Messages with unresolvable timestamps show `[unknown]`.

## WAL / recency caveat

The most recent messages (sent in the last few minutes) may live in the WAL
(`.log` file) rather than compacted `.ldb` SSTables. If a very recent message
is missing:

1. Wait 2–5 minutes while Teams is active (write volume triggers compaction)
2. Recopy: `cp -r <cache-path> /tmp/teams_copy`
3. Re-run the extractor

The script scans both `.ldb` and `.log` files, but WAL extraction is less
reliable for the most recent message in an active session.

## Display name lookup

`--from-user` matches on the display name string embedded in message blobs.
Use the exact name as it appears in Teams (e.g. `'Jane Doe'`, not `'Doe'`
or `'jane.doe@example.com'`). If unsure, omit `--from-user` and use `--search`
with a unique phrase from the person to locate them.

## Common patterns

### Pre meeting context check
```bash
cp -r ~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb /tmp/teams_copy
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --from-user 'Person Name' \
  --recent 30 \
  --output /tmp/teams_person.txt
cat /tmp/teams_person.txt
```

### Search across all recent activity
```bash
cp -r ~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb /tmp/teams_copy
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --search 'topic or keyword' \
  --recent 20
```

## Limitations

- Read-only — no send, reply, or organize capability
- Local cache only — history limited to what Chromium has cached (typically weeks)
- Received messages rely on display name matching; partial names may miss results
- Chromium Teams only — native Teams app uses a different cache path
