---
name: teams-extractor
description: >
  Read Microsoft Teams messages from the local Chromium IndexedDB cache or
  native Teams app cache — no API auth, no Entra app, no admin permissions
  required. Works with the Chromium web app (teams.cloud.microsoft) on macOS
  or Linux, and with the native Teams desktop app (WebView2-based,
  teams.microsoft.com) on macOS — Microsoft discontinued the official native
  Linux client in 2022. Use this skill whenever the user wants to retrieve
  Teams messages, check what someone said in Teams, search Teams chat
  history, or capture a Teams message as a note. Trigger on: "check my
  Teams", "what did [person] say in Teams", "find [person]'s message about
  [topic] in Teams", "Teams DM from [person]", "capture that Teams message",
  or any request to read or search Teams chat history. Do NOT use for
  sending messages — read-only.
compatibility: Requires uv (for python-snappy). Native Teams desktop app cache works on macOS only (Microsoft discontinued the Linux client in 2022). Chromium web app cache works on both macOS and Linux.
license: MIT
---

# Teams Extractor

Reads Microsoft Teams messages directly from the local LevelDB cache.
No auth setup. No API calls. Works offline. Zero IT footprint.

Works with two Teams deployment types:
- **Chromium web app** — Teams opened in a Chromium browser at `teams.cloud.microsoft` (macOS or Linux)
- **Native desktop app** — The Microsoft Teams 2.x app (WebView2-based), available on **macOS only**. Microsoft discontinued the official native Linux client in 2022, replacing it with the web/PWA app. On Linux, use the Chromium web app path instead.

## Available scripts

- **`scripts/teams_extractor.py`** — Extracts messages from a copied LevelDB
  cache. Supports filtering by sender display name, keyword search, and recency.
  Self-contained via PEP 723 inline deps — run with `uv run`.

## Prerequisites

- Teams must have been opened recently (cache must be populated)
- `uv` must be available (`which uv`) — it handles `python-snappy` automatically

---

## Step 1 — Locate and copy the cache

**Always probe first** — don't assume which app type is in use. Run the
discovery snippet below, then copy whichever path resolves.

### Cache path discovery (run this first)

```bash
# --- macOS ---
# Chromium web app (teams.cloud.microsoft)
CHROMIUM_MAC=~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb
# Native Teams desktop app (WebView2, teams.microsoft.com)
NATIVE_MAC="$HOME/Library/Containers/com.microsoft.teams2/Data/Library/Application Support/Microsoft/MSTeams/EBWebView/WV2Profile_tfw/IndexedDB/https_teams.microsoft.com_0.indexeddb.leveldb"

# --- Linux ---
# Chromium web app (the only supported path on Linux — Microsoft discontinued
# the native Linux client in 2022; the WebView2 native app is macOS-only)
CHROMIUM_LINUX=~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb

# Auto-detect: try all known paths, use first that exists
for p in "$NATIVE_MAC" "$CHROMIUM_MAC" "$CHROMIUM_LINUX"; do
  if [ -d "$p" ]; then
    echo "Found: $p"
    TEAMS_CACHE="$p"
    break
  fi
done
echo "Using: $TEAMS_CACHE"
```

### Quick reference table

| OS | App type | Cache path |
|----|----------|------------|
| macOS | **Native desktop app** | `~/Library/Containers/com.microsoft.teams2/Data/Library/Application Support/Microsoft/MSTeams/EBWebView/WV2Profile_tfw/IndexedDB/https_teams.microsoft.com_0.indexeddb.leveldb` |
| macOS | Chromium web app | `~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb` |
| Linux | Chromium web app (only supported path) | `~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb` |

> **Linux note:** Microsoft discontinued the official native Teams Linux
> client in 2022 in favor of the web app / PWA. There is no WebView2-based
> native app cache to read on Linux. If the user runs an unofficial
> third-party Electron wrapper (e.g. `teams-for-linux`), its cache is not
> guaranteed to share the same IndexedDB structure — treat it as unverified
> and fall back to the Chromium web app path if extraction fails.

> **Key distinction:** Chromium web app uses `https_teams.cloud.microsoft` in the path.
> Native desktop app uses `https_teams.microsoft.com`. Don't mix them up.

### Copy the cache

Teams holds a write lock on the LevelDB directory. Always copy first:

```bash
cp -r "$TEAMS_CACHE" /tmp/teams_copy
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

### Pre-meeting context check
```bash
# 1. Auto-detect cache (see Step 1 above), then:
cp -r "$TEAMS_CACHE" /tmp/teams_copy
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --from-user 'Person Name' \
  --recent 30 \
  --output /tmp/teams_person.txt
cat /tmp/teams_person.txt
```

### Search across all recent activity
```bash
cp -r "$TEAMS_CACHE" /tmp/teams_copy
uv run scripts/teams_extractor.py /tmp/teams_copy \
  --search 'topic or keyword' \
  --recent 20
```

### Full discovery + copy one-liner (macOS native app)
```bash
cp -r "$HOME/Library/Containers/com.microsoft.teams2/Data/Library/Application Support/Microsoft/MSTeams/EBWebView/WV2Profile_tfw/IndexedDB/https_teams.microsoft.com_0.indexeddb.leveldb" /tmp/teams_copy
```

### Full discovery + copy one-liner (Linux, Chromium web app)
```bash
cp -r ~/.config/chromium/Default/IndexedDB/https_teams.cloud.microsoft_0.indexeddb.leveldb /tmp/teams_copy
```

## Limitations

- Read-only — no send, reply, or organize capability
- Local cache only — history limited to what the app has cached (typically weeks)
- Received messages rely on display name matching; partial names may miss results
- Cache must exist on disk — Teams must have been opened at least once on this machine
