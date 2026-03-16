# Inbox analytics — sender histogram

Renders a terminal histogram of top Gmail senders. Default query: `is:unread`
(all time, all folders, excludes spam/trash). Results are cached in SQLite so
large inboxes (200k+ messages) can run overnight and resume if interrupted.

## Usage

```bash
python3 skills/gmail-inbox/scripts/histogram.py [flags]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--months N` | — | Lookback period (overrides default `is:unread`) |
| `--top N` | 20 | Number of senders to show |
| `--query Q` | — | Override with any Gmail search query |
| `--account A` | — | gws account (omit for default) |
| `--no-fetch` | — | Render from cache only, no API calls |
| `--refresh` | — | Clear cache and re-fetch everything |
| `--mark-read PATTERN` | — | Mark all cached messages from sender as read |
| `--trash PATTERN` | — | Move all cached messages from sender to trash |
| `--yes` | — | Skip confirmation for `--mark-read` / `--trash` |

## Examples

```bash
# Overnight run: fetch all unread messages (210k → ~70 min first run)
python3 skills/gmail-inbox/scripts/histogram.py

# Re-render from cache after overnight run completes (instant)
python3 skills/gmail-inbox/scripts/histogram.py --no-fetch

# Show top 50 senders
python3 skills/gmail-inbox/scripts/histogram.py --no-fetch --top 50

# Last 6 months instead of all unread
python3 skills/gmail-inbox/scripts/histogram.py --months 6

# Cleanup: mark all GitHub notification emails as read (prompts for confirmation)
python3 skills/gmail-inbox/scripts/histogram.py --mark-read "*@github.com"

# Cleanup: trash a specific newsletter sender
python3 skills/gmail-inbox/scripts/histogram.py --trash "newsletter@example.com"
```

## Sender pattern syntax

`--mark-read` and `--trash` accept glob patterns matched against the From address:

| Pattern | Matches |
|---------|---------|
| `user@example.com` | exact address |
| `*@github.com` | any GitHub sender |
| `noreply*` | any noreply address |

Both commands show a count and ask for confirmation before acting. Use `--yes`
to skip the prompt.

## Performance

- **First run (210k messages)**: ~70 min. Runs safely overnight with progress bar + ETA.
- **Subsequent runs**: seconds (only new/uncached messages are fetched).
- **Interrupted runs**: safe to restart — already-cached messages are skipped.
- **Cache location**: `~/.cache/gmail-histogram/{account}.db`
- **Token refresh**: access tokens auto-refresh every ~58 min (no manual action needed).
