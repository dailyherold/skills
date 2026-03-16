---
name: gmail-inbox
description: >
  Reads, searches, sends, replies, forwards, drafts, archives, moves, labels,
  and organizes Gmail (Google Workspace) via the gws CLI. Use this skill
  whenever the user mentions Gmail, their Google inbox, Google Workspace email,
  or any email task that involves a @gmail.com address or Google account — even
  if they don't say "gws" or ask explicitly about email tooling. Also trigger
  for Gmail inbox triage, searching by sender or subject, bulk organizing,
  watching for new mail, and inbox analytics — including top senders, sender
  histograms, "who emails me most", breakdown by sender, and bulk cleanup by
  sender pattern (mark-read, trash).
---

# Gmail — gws CLI

All operations go through `gws gmail`. Auth must be set up first.

## Prerequisites

```bash
gws auth login   # browser-based OAuth, one-time per machine
```

## Your From address

Before sending, replying, drafting, or forwarding — resolve your email address. Gmail will reject messages with a mismatched or missing From header.

```bash
_from=$(gws gmail users getProfile --params '{"userId":"me"}' --format json 2>/dev/null | jq -r '.emailAddress')
# e.g. you@gmail.com
```

---

## Command structure

| Use case | Tool |
|----------|------|
| Quick inbox summary | `gws gmail +triage` |
| Simple send | `gws gmail +send` |
| Everything else (read, search, reply, organize) | `gws gmail users <resource> <method> --params '{"userId":"me",...}'` |

---

## JSON output

- Always use `--format json` unless the user explicitly wants human-readable output.
- Always append `2>/dev/null` because `gws` writes a keyring diagnostic to stderr on every invocation that will break parsers:

```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread"}' --format json 2>/dev/null | jq .
```

**Debug Note:** Remove `2>/dev/null` temporarily if commands return empty or unexpected output — real errors (auth failures, bad params) also go to stderr and will be hidden otherwise.

---

## Listing and reading

```bash
# Unread inbox summary (sender, subject, date)
gws gmail +triage
gws gmail +triage --max 50 --query 'from:boss@example.com'

# List messages (returns IDs only — get full content separately)
gws gmail users messages list --params '{"userId":"me","q":"is:unread"}'
gws gmail users messages list --params '{"userId":"me","q":"from:alice@example.com","maxResults":20}'

# Get full message by ID
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' --format json

# The response body parts are base64url-encoded. Decode the snippet or parts[].body.data:
# echo "$_msg" | jq -r '.payload.parts[0].body.data' | tr '_-' '/+' | base64 -d
# For simple messages, .payload.body.data works directly instead of .parts[0]

# List threads
gws gmail users threads list --params '{"userId":"me","q":"subject:meeting"}'
gws gmail users threads get --params '{"userId":"me","id":"THREAD_ID"}'
```

Gmail message IDs are globally stable — not folder-scoped.

---

## Searching

Gmail uses a search query string (`q` param) that matches the Gmail search box.

```bash
# Common query patterns
gws gmail users messages list --params '{"userId":"me","q":"from:sender@example.com"}'
gws gmail users messages list --params '{"userId":"me","q":"subject:invoice after:2026/01/01"}'
gws gmail users messages list --params '{"userId":"me","q":"is:unread label:INBOX"}'
gws gmail users messages list --params '{"userId":"me","q":"has:attachment filename:pdf"}'
gws gmail users messages list --params '{"userId":"me","q":"in:sent to:alice@example.com"}'
```

### Gmail search operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `from:` | `from:alice@example.com` | Sender |
| `to:` | `to:bob@example.com` | Recipient |
| `subject:` | `subject:invoice` | Subject contains |
| `label:` | `label:work` | Has label |
| `is:unread` | | Unread messages |
| `is:starred` | | Starred messages |
| `after:` | `after:2026/01/01` | After date |
| `before:` | `before:2026/03/01` | Before date |
| `has:attachment` | | Has attachment |
| `in:inbox` | | In inbox folder |
| `in:sent` | | In sent folder |
| `-` | `-from:noreply` | Negate any operator |

---

## Sending

```bash
# Simple send
gws gmail +send --to recipient@example.com --subject 'Hello' --body 'Hi there!'

# With CC/BCC or HTML body — use raw API with base64-encoded RFC 2822 message
_raw=$(printf 'From: $_from\r\nTo: recipient@example.com\r\nSubject: Hello\r\nContent-Type: text/plain\r\n\r\nBody here.' | base64 | tr -d '\n')
gws gmail users messages send --params '{"userId":"me"}' --json "{\"raw\":\"$_raw\"}"
```

> Confirm with user before sending.

---

## Reply

Threading in Gmail relies on `In-Reply-To`/`References` headers AND the `threadId` field.

```bash
# Step 1: get the original message to extract headers
_msg=$(gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' --format json 2>/dev/null)

# Step 2: extract needed fields (adjust jq paths based on actual response structure)
_thread_id=$(echo "$_msg" | jq -r '.threadId')
_msg_id=$(echo "$_msg" | jq -r '.payload.headers[] | select(.name=="Message-ID") | .value')
_from=$(echo "$_msg" | jq -r '.payload.headers[] | select(.name=="From") | .value')
_subject=$(echo "$_msg" | jq -r '.payload.headers[] | select(.name=="Subject") | .value')

# Step 3: compose reply with threading headers
_raw=$(printf "From: $_from\r\nTo: $_from\r\nSubject: Re: $_subject\r\nIn-Reply-To: $_msg_id\r\nReferences: $_msg_id\r\nContent-Type: text/plain\r\n\r\nReply body here." | base64 | tr -d '\n')

# Step 4: send with threadId to keep in thread
gws gmail users messages send --params '{"userId":"me"}' --json "{\"raw\":\"$_raw\",\"threadId\":\"$_thread_id\"}"
```

For deeper threads, `References` should list all prior Message-IDs space-separated; `In-Reply-To` is always just the immediate parent.

---

## Forward

Forward is a fresh send with no `In-Reply-To`/`References`. Read the original first, then compose:

```bash
# Read original to get subject/body
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' --format json 2>/dev/null

# Compose and send forward
_raw=$(printf "From: $_from\r\nTo: newrecipient@example.com\r\nSubject: Fwd: Original Subject\r\nContent-Type: text/plain\r\n\r\n[Optional preamble.]\r\n\r\n--- Forwarded message ---\r\nFrom: original@example.com\r\nSubject: Original Subject\r\n\r\nOriginal body here." | base64 | tr -d '\n')
gws gmail users messages send --params '{"userId":"me"}' --json "{\"raw\":\"$_raw\"}"
```

---

## Drafts

```bash
# Create draft
_raw=$(printf "From: $_from\r\nTo: recipient@example.com\r\nSubject: Draft subject\r\nContent-Type: text/plain\r\n\r\nDraft body." | base64 | tr -d '\n')
gws gmail users drafts create --params '{"userId":"me"}' --json "{\"message\":{\"raw\":\"$_raw\"}}"

# List drafts
gws gmail users drafts list --params '{"userId":"me"}'

# Get draft
gws gmail users drafts get --params '{"userId":"me","id":"DRAFT_ID"}'

# Send draft
gws gmail users drafts send --params '{"userId":"me"}' --json '{"id":"DRAFT_ID"}'
```

---

## Organizing

Gmail labels are the organizing primitive. System labels: `INBOX`, `UNREAD`, `STARRED`, `IMPORTANT`, `TRASH`, `SPAM`, `SENT`.

```bash
# Archive (remove from inbox — message stays in All Mail)
gws gmail users messages modify \
  --params '{"userId":"me","id":"MSG_ID"}' \
  --json '{"removeLabelIds":["INBOX"]}'

# Move to trash
gws gmail users messages trash --params '{"userId":"me","id":"MSG_ID"}'

# Restore from trash
gws gmail users messages untrash --params '{"userId":"me","id":"MSG_ID"}'

# Mark as read
gws gmail users messages modify \
  --params '{"userId":"me","id":"MSG_ID"}' \
  --json '{"removeLabelIds":["UNREAD"]}'

# Mark as unread
gws gmail users messages modify \
  --params '{"userId":"me","id":"MSG_ID"}' \
  --json '{"addLabelIds":["UNREAD"]}'

# Star
gws gmail users messages modify \
  --params '{"userId":"me","id":"MSG_ID"}' \
  --json '{"addLabelIds":["STARRED"]}'

# Apply a custom label
gws gmail users messages modify \
  --params '{"userId":"me","id":"MSG_ID"}' \
  --json '{"addLabelIds":["LABEL_ID"]}'

# Modify multiple messages at once (batch modify)
gws gmail users messages batchModify \
  --params '{"userId":"me"}' \
  --json '{"ids":["ID1","ID2"],"addLabelIds":["LABEL_ID"],"removeLabelIds":["INBOX"]}'
```

> Confirm before bulk operations.

---

## Labels

```bash
# List all labels (get IDs for custom labels)
gws gmail users labels list --params '{"userId":"me"}' --format json 2>/dev/null

# Get label details
gws gmail users labels get --params '{"userId":"me","id":"LABEL_ID"}'

# Create label
gws gmail users labels create \
  --params '{"userId":"me"}' \
  --json '{"name":"my-label","labelListVisibility":"labelShow","messageListVisibility":"show"}'
```

Custom label IDs look like `Label_XXXXXXXXXX`. Always list labels to get the ID before using it in modify operations.

---

## Watch for new mail

Streams new messages as NDJSON (requires GCP project for Pub/Sub):

```bash
gws gmail +watch --project my-gcp-project
gws gmail +watch --project my-project --label-ids INBOX --once
gws gmail +watch --project my-project --cleanup   # delete Pub/Sub resources on exit
```

---

## Guardrails

- Confirm with user before any send, reply, forward, or bulk organize
- Prefer trash over permanent delete
- List labels first rather than guessing IDs
- Use `--dry-run` to validate operations before executing

---

## Inbox analytics

For sender histograms, top-sender analysis, and bulk cleanup by sender pattern, see [inbox-analytics.md](inbox-analytics.md).
