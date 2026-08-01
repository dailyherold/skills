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
compatibility: Requires uv and git. See "Maintenance: updating the pinned engine version" and scripts/vendor/VENDORED.md for how the dependency chain is pinned and maintained. Native Teams desktop app cache works on macOS only (Microsoft discontinued the Linux client in 2022). Chromium web app cache works on both macOS and Linux.
license: MIT
---

# Teams Extractor

Reads Microsoft Teams messages directly from the local IndexedDB LevelDB
cache. No auth setup. No API calls. Works offline. Zero IT footprint.

Parsing is delegated to
[ccl_chromium_reader](https://github.com/cclgroupltd/ccl_chromium_reader), a
proper LevelDB + V8 deserialization library, rather than scanning raw bytes
for marker strings. That means messages arrive as fully structured data
(correct field names, nested objects), and both compacted `.ldb` files and the
write-ahead log (`.log`) are parsed with the same reliability — there's no
separate "recent messages might be missing" caveat to work around.

Works with two Teams deployment types:
- **Chromium web app** — Teams opened in a Chromium browser at `teams.cloud.microsoft` (macOS or Linux)
- **Native desktop app** — The Microsoft Teams 2.x app (WebView2-based), available on **macOS only**. Microsoft discontinued the official native Linux client in 2022, replacing it with the web/PWA app. On Linux, use the Chromium web app path instead.

## Available scripts

- **`scripts/teams_extractor.py`** — Extracts messages from a copied
  IndexedDB LevelDB cache. Supports filtering by sender display name, keyword
  search, and recency. Self-contained via PEP 723 inline deps — run with
  `uv run`.
- **`scripts/vendor/`** — A vendored dependency and the notes on why it's
  vendored and how to maintain it. Not something you need to touch to run the
  skill; see "Maintenance: updating the pinned engine version" below if the
  pinned engine version ever needs bumping.

## Prerequisites

- Teams must have been opened recently (cache must be populated)
- `uv` must be available (`which uv`)
- `git` must be available (`which git`) — `uv` uses it to fetch the pinned
  `ccl_chromium_reader` engine, which isn't published on PyPI. First run
  needs network access to fetch it and its PyPI dependencies; after that,
  `uv`'s cache makes subsequent runs fast and offline.

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

The native macOS app also has a sibling `.blob` directory (same name, ending
in `.blob` instead of `.leveldb`) holding externally-stored large message
values. Copy it too if present, alongside the `.leveldb` copy:

```bash
BLOB_DIR="${TEAMS_CACHE%.leveldb}.blob"
[ -d "$BLOB_DIR" ] && cp -r "$BLOB_DIR" /tmp/teams_blob_copy
```

The script auto-detects `/tmp/teams_blob_copy` if it sits next to
`/tmp/teams_copy` with the expected naming; pass `--blob-path` explicitly if
you copy it elsewhere.

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
| `--from-user NAME` | Only messages from this display name. Without this, only your own sent messages are returned. |
| `--search WORD` | Only messages containing this text (case-insensitive). |
| `--recent N` | Only the N most recent matching messages. |
| `--blob-path PATH` | Sibling `.blob` directory for externally-stored values (auto-detected by default). |
| `--output FILE` | Write results to a file instead of stdout. |

## Output format

One line per message:

```
[YYYY-MM-DDTHH:MM:SS] message text
```

Timestamps are UTC. Messages with unresolvable timestamps show `[unknown]`.

## Display name lookup

`--from-user` matches on the display name as stored in the message record.
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

### Full discovery + copy one-liner (macOS native app, with blob dir)
```bash
BASE="$HOME/Library/Containers/com.microsoft.teams2/Data/Library/Application Support/Microsoft/MSTeams/EBWebView/WV2Profile_tfw/IndexedDB"
cp -r "$BASE/https_teams.microsoft.com_0.indexeddb.leveldb" /tmp/teams_copy
cp -r "$BASE/https_teams.microsoft.com_0.indexeddb.blob" /tmp/teams_blob_copy
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
- First run needs network access (to fetch the pinned `ccl_chromium_reader`
  engine and its PyPI dependencies); offline after that via `uv`'s cache

## Maintenance: updating the pinned engine version

The parsing engine (`ccl_chromium_reader`) is pinned to a specific commit in
`scripts/teams_extractor.py`'s PEP 723 header, not a version range — this
repo doesn't publish releases, so a commit hash is the only stable reference.
Only repin it if something breaks (e.g. Teams changes its IndexedDB schema in
a way the current pin can't parse) or you deliberately want a newer commit's
fixes. There's no routine update cadence.

To repin:

1. Pick the new commit from https://github.com/cclgroupltd/ccl_chromium_reader/commits/master
2. Update the `ccl_chromium_reader @ git+...@<commit>` line in
   `scripts/teams_extractor.py`'s `dependencies` list to the new commit hash.
3. **Read `scripts/vendor/VENDORED.md` and follow its "Maintenance" section**
   — the new commit's `pyproject.toml` may pin a different `ccl_simplesnappy`
   commit than the one vendored here, and the override in the PEP 723 header
   won't warn you if it's now out of sync.
4. Re-run the extractor against a real (copied) cache and confirm message
   counts and content look sane before trusting the new pin — see Step 2
   above for example invocations.
