---
name: proton-inbox
description: Reads, searches, sends, replies, forwards, archives, moves, and organizes Proton Mail email via himalaya CLI and Proton Mail Bridge. Use this skill whenever the user mentions email, their inbox, Proton Mail, messages from someone, unread mail, drafts, or wants to send/reply/forward anything — even if they don't say "himalaya" or ask explicitly about email tooling.
compatibility: opencode
---

# Proton Mail — himalaya CLI

Himalaya connects to Proton Mail Bridge on localhost.

**Two flags required on every command:** `--account proton --output json`
Exception: organizing commands (`move`, `flag add/remove`) produce no meaningful output — omit `--output json` there.

## Prerequisites

- Proton Mail Bridge
- himalaya

## Your From address

Before sending, replying, drafting, or forwarding — resolve your display name and
email address. Bridge will reject messages missing the From header.

```bash
_name=$(grep 'display-name' ~/.config/himalaya/config.toml | head -1 | sed 's/.*= "\(.*\)"/\1/')
_email=$(grep '^email' ~/.config/himalaya/config.toml | head -1 | sed 's/.*= "\(.*\)"/\1/')
_from="$_name <$_email>"
# e.g. "Gary Proton <gary@proton.example>"
```

## Listing and reading

```bash
himalaya folder list --account proton
himalaya envelope list --output json --account proton
himalaya envelope list --output json --account proton --folder Sent
himalaya envelope list --output json --account proton --page 2 --page-size 50
himalaya message read --output json --account proton <id>

# IDs are folder-scoped — if the ID came from a --folder search, pass the same --folder here
himalaya message read --output json --account proton --folder "All Mail" <id>
```

## Envelope JSON shape

`envelope list` returns a **JSON array**. Key fields per envelope:
- `id` — string
- `subject` — string
- `date` — string
- `flags` — array of strings e.g. `["Seen"]`, empty array if none
- `from` / `to` — **objects** with `name` (nullable) and `addr` fields, not arrays
- `has_attachment` — boolean

```bash
# correct jq — from/to are objects, not arrays
himalaya envelope list --output json --account proton | jq -r '.[] | "\(.id)\t\(.from.name // .from.addr)\t\(.subject)"'
```

## Searching

All flags must come **before** query terms — query is a variadic positional arg.

Default folder is `INBOX`. For broad searches across all email use `--folder "All Mail"`.

Multi-word values must be quoted **within** the query and passed as a single shell argument:
```bash
# single word — no inner quotes needed
himalaya envelope list --output json --account proton subject Encanto

# multi-word — inner quotes, whole query as one shell arg
himalaya envelope list --output json --account proton 'subject "El Encanto"'

# search all mail
himalaya envelope list --output json --account proton --folder "All Mail" 'subject "El Encanto"'
```

```bash
# From a specific sender ("from" = sender only, not date)
himalaya envelope list --output json --account proton from "sender@example.com"

# By subject keyword
himalaya envelope list --output json --account proton 'subject "invoice keyword"'

# Unread only
himalaya envelope list --output json --account proton not flag seen

# On a specific date
himalaya envelope list --output json --account proton date 2024-03-15

# Unread on a specific date
himalaya envelope list --output json --account proton date 2024-03-15 and not flag seen

# Most recent first
himalaya envelope list --output json --account proton order by date desc
```

### Query DSL

| Condition | Meaning |
|-----------|---------|
| `date <yyyy-mm-dd>` | exact date |
| `before <yyyy-mm-dd>` | strictly before date |
| `after <yyyy-mm-dd>` | strictly after date |
| `from <pattern>` | sender address/name (**not** date) |
| `to <pattern>` | recipient address/name |
| `subject <pattern>` | subject line |
| `body <pattern>` | text body |
| `flag <flag>` | has flag: `seen` `answered` `flagged` `deleted` `draft` — note: `flagged` = starred in Proton UI |

Operators: `not`, `and`, `or`. Sort: `order by date|from|to|subject [asc|desc]`.

## Composing and sending

```bash
# Reuse in all send/draft/reply/forward commands
_date=$(date -R 2>/dev/null || date '+%a, %-d %b %Y %T %z')

# New message (fresh thread)
cat <<EOF | himalaya message send --account proton
From: $_from
To: recipient@example.com
Subject: Hello
Date: $_date

Body here.
EOF
```

### Reply

Proton groups messages by `In-Reply-To`/`References` headers, not just subject — always
include them when replying.

```bash
# Extract Message-ID via raw export — message read --output json returns plain text, not structured data
# (pimalaya/himalaya#477: once structured JSON export lands, this can use jq instead)
_msg_id=$(himalaya message export --full --account proton <id> 2>/dev/null \
  | grep -i "^message-id:" | sed 's/^[Mm]essage-[Ii][Dd]: //')

cat <<EOF | himalaya message send --account proton
From: $_from
To: original-sender@example.com
Subject: Re: Original subject
Date: $_date
In-Reply-To: $_msg_id
References: $_msg_id

Reply body here.
EOF
```

For deeper threads, `References` should list all prior Message-IDs in order (space-separated). `In-Reply-To` is always just the immediate parent.

### Forward

Forwarding is a fresh send (no `In-Reply-To`/`References`). Read the original first to
get its headers and body, then compose:

```bash
# Read original
himalaya message read --output json --account proton <id>

# Forward it
cat <<EOF | himalaya message send --account proton
From: $_from
To: new-recipient@example.com
Subject: Fwd: Original subject
Date: $_date

[Optional preamble here.]

--- Forwarded message ---
From: original-sender@example.com
Date: <original date>
Subject: Original subject
To: <original to>

<original body here>
EOF
```

## Drafts

```bash
# New draft (fresh thread)
cat <<EOF | himalaya message save --account proton --folder Drafts
From: $_from
To: recipient@example.com
Subject: Subject here
Date: $_date

Body here.
EOF

# Reply draft (threads correctly in Proton — see Reply section for how to get _msg_id)
cat <<EOF | himalaya message save --account proton --folder Drafts
From: $_from
To: original-sender@example.com
Subject: Re: Original subject
Date: $_date
In-Reply-To: $_msg_id
References: $_msg_id

Reply body here.
EOF
```

## Organizing

```bash
# Move — TARGET folder before ID; use -f/--folder to specify non-INBOX source
himalaya message move Archive --account proton <id>
himalaya message move Trash --account proton <id>
himalaya message move "Labels/label-name" --account proton <id>

himalaya flag add --account proton <id> seen      # mark read
himalaya flag remove --account proton <id> seen   # mark unread
himalaya flag add --account proton <id> flagged   # star (flagged = starred in Proton UI)
himalaya flag remove --account proton <id> flagged # unstar
```

## Folders vs Labels (Proton model)

**Folders** are mutually exclusive — a message lives in exactly one real folder (Inbox, Archive, etc.). Moving to a folder relocates the message.

**Labels** are tags — a message keeps its folder location and can carry multiple labels simultaneously. Via Bridge, labels surface as IMAP folders under `Labels/<name>`, but IMAP folder operations against them are translated into tag add/remove, not relocation:

- **Moving INTO** `Labels/<name>` applies the label. The message stays in its real folder (INBOX etc.) AND appears in the label folder view.
- **Moving OUT OF** `Labels/<name>` (to a real folder) removes the label. The message stays wherever it already was.
- **Copying** into a label folder also applies the label — useful when the source is already a label folder and you want to add a second label without disturbing the first.

```bash
# Apply label — message stays in INBOX, also appears in label view
himalaya message move "Labels/my-label" --account proton <id>

# Apply label to multiple messages at once
himalaya message move "Labels/my-label" --account proton <id1> <id2>

# Add a second label (source is already a label folder — copy keeps both)
himalaya message copy "Labels/second-label" --account proton --folder "Labels/first-label" <id>

# Remove label (move out of label folder to any real folder)
himalaya message move INBOX --account proton --folder "Labels/my-label" <id>

# List messages with a label
himalaya envelope list --output json --account proton --folder "Labels/my-label"

# Create a new label
himalaya folder add "Labels/my-new-label" --account proton
```

**Limitations:**
- One target per command — applying two labels requires two commands
- No way to query which labels a message currently has — envelope `flags` only reflect IMAP flags (`seen`, `flagged`, etc.), raw headers carry no label metadata. The only option is scanning each `Labels/*` folder, which makes one IMAP round-trip per label. Do not do this unless the user explicitly asks and understands it will check every label folder.

> **Warning:** Client-side tag features in email clients (e.g. Thunderbird "Tags") are **not** Proton labels — they do not sync to Proton servers. Only IMAP operations against `Labels/*` paths have effect.

## Folder names (via Bridge)

| Proton UI         | IMAP name          | Notes |
|-------------------|--------------------|-------|
| Inbox             | `INBOX`            | |
| Sent              | `Sent`             | |
| Drafts            | `Drafts`           | |
| Trash             | `Trash`            | |
| Spam              | `Spam`             | |
| Archive           | `Archive`          | |
| All Mail          | `All Mail`         | Read-only view of every message |
| Starred           | `Starred`          | Messages flagged with `flagged` flag |
| Any label         | `Labels/<name>`    | |
| Any custom folder | `Folders/<name>`   | Proton UI Folders (not labels) |

Always run `himalaya folder list --account proton` to confirm exact names — Bridge versions may vary.

## Guardrails

- Confirm before bulk-moving or deleting multiple messages
- Prefer `Trash` over permanent deletion
- List folders first rather than guessing names
- Never run `reply`, `write`, or `forward` without piping — they block on `$EDITOR`

## Bridge caveats

- Bridge uses StartTLS on IMAP (1143) and SMTP (1025)
- himalaya password is the Bridge app password, **not** your Proton account password
- **Sending works via the Sendmail backend** (`msmtp -t`) — `himalaya message send` routes
  through msmtp automatically. No direct msmtp invocation needed. himalaya's lettre SMTP
  backend hard-rejects Bridge's self-signed cert regardless of config (pimalaya/himalaya#493),
  which is why Sendmail is used instead.
- **IMAP uses cert fingerprint pinning** — requires `~/.config/protonmail/bridge-cert.pem`
  to exist (one-time export per machine)
- If connection fails, verify Bridge is running and logged in
- Message IDs are folder-scoped — re-list after switching folders
