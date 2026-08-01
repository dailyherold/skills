#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "ccl_chromium_reader @ git+https://github.com/cclgroupltd/ccl_chromium_reader.git@9639a318ce0f7b546e1d8d02d89423ab6b4ae202",
#   "beautifulsoup4>=4.12",
#   "ccl_simplesnappy",
# ]
# requires-python = ">=3.11"
#
# # ccl_simplesnappy is vendored (see vendor/VENDORED.md) because
# # ccl_chromium_reader pins it to an unpinned git HEAD upstream.
# [tool.uv.sources]
# ccl_simplesnappy = { path = "./vendor/ccl_simplesnappy_pkg" }
#
# [tool.uv]
# override-dependencies = ["ccl_simplesnappy"]
# ///
"""
Extract Microsoft Teams messages from a local IndexedDB LevelDB cache.

Parsing is delegated to ccl_chromium_reader, which handles LevelDB SSTable +
WAL framing and V8 deserialization, so Teams records arrive as real Python
dicts rather than byte blobs. This script only locates the message-bearing
object stores, normalizes each message, and filters.

Teams holds a write lock on the cache, so copy it before reading:
  cp -r "<leveldb-path>" /tmp/teams_copy

Usage:
  uv run teams_extractor.py /tmp/teams_copy [--from-user NAME] [--search WORD]
                            [--recent N] [--blob-path PATH] [--output FILE]

With no --from-user, only messages sent by the current user are returned.
Output is one line per message: [YYYY-MM-DDTHH:MM:SS] text

See ../SKILL.md for cache locations per platform.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    from ccl_chromium_reader import ccl_chromium_indexeddb
except ImportError:
    sys.exit("Missing dependencies — run this script with `uv run` so its inline deps install.")

# Teams splits data across many per-manager IndexedDB databases. These are the
# object stores whose records carry a 'messageMap' of message id -> message.
MESSAGE_STORES = frozenset({"replychains", "threads", "saved", "drafts", "mentions"})

# Message fields tried in order when resolving a sender's display name.
SENDER_FIELDS = ("imDisplayName", "fromDisplayNameInToken", "creator")

# Message fields tried in order when resolving a timestamp (epoch milliseconds).
TIME_FIELDS = ("originalArrivalTime", "clientArrivalTime")

DEDUP_PREFIX_LEN = 200


def as_text(value) -> str | None:
    """Coerce a V8-deserialized string field to str.

    The V8 deserializer returns raw bytes for "one-byte strings" that aren't
    pure ASCII rather than guessing an encoding. Those bytes are Latin-1 per
    the V8 spec, which matters for names like 'João' and 'Noé'.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("latin-1", errors="replace")
    return None


def clean_html(html: str) -> str:
    """Reduce a Teams HTML message body to a single line of plain text."""
    text = BeautifulSoup(html, features="html.parser").get_text(separator=" ")
    return " ".join(text.split())


def epoch_ms_to_iso(value) -> str | None:
    """Format epoch milliseconds as an ISO-8601 UTC timestamp."""
    if not isinstance(value, (int, float)) or value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, OverflowError, OSError):
        return None


def first_field(msg: dict, fields, transform) -> str | None:
    """Return the first field in `fields` that `transform` resolves truthily."""
    for field in fields:
        result = transform(msg.get(field))
        if result:
            return result
    return None


def find_blob_path(leveldb_dir: Path) -> Path | None:
    """Locate the sibling .blob directory holding externally-stored values."""
    if leveldb_dir.name.endswith(".leveldb"):
        candidate = leveldb_dir.with_name(leveldb_dir.name[: -len(".leveldb")] + ".blob")
        if candidate.is_dir():
            return candidate
    return None


def iter_raw_messages(ldb_dir: Path, blob_dir: Path | None):
    """Yield raw Teams message dicts from every message store in the cache."""
    wrapper = ccl_chromium_indexeddb.WrappedIndexDB(ldb_dir, blob_dir)

    for db_info in wrapper.database_ids:
        if db_info.dbid_no is None:
            continue
        db = wrapper[db_info.dbid_no]

        for store_name in db.object_store_names:
            if store_name not in MESSAGE_STORES:
                continue

            # A handler is required to skip records that fail V8
            # deserialization. Wrapping next() in try/except instead would
            # silently drop every record after the first failure, since a
            # generator stops permanently once it raises.
            records = db[store_name].iterate_records(
                bad_deserializer_data_handler=lambda *_: None
            )
            for record in records:
                if not isinstance(record.value, dict):
                    continue
                message_map = record.value.get("messageMap")
                if not isinstance(message_map, dict):
                    continue
                for msg in message_map.values():
                    if isinstance(msg, dict) and msg.get("content"):
                        yield msg


def normalize(msg: dict) -> dict | None:
    """Flatten a raw Teams message into {timestamp, sender, text, is_sent}."""
    content = as_text(msg.get("content"))
    if not content:
        return None

    text = clean_html(content)
    if not text:
        return None

    return {
        "timestamp": first_field(msg, TIME_FIELDS, epoch_ms_to_iso) or "unknown",
        "sender": first_field(msg, SENDER_FIELDS, as_text) or "unknown",
        "text": text,
        "is_sent": bool(msg.get("isSentByCurrentUser")),
    }


def extract(ldb_dir: Path, blob_dir: Path | None, from_user: str | None = None,
            search: str | None = None) -> list[dict]:
    """Extract, filter, and dedupe messages, oldest first."""
    sent_only = from_user is None
    from_user = from_user.lower() if from_user else None
    search = search.lower() if search else None

    seen = set()
    messages = []

    for raw in iter_raw_messages(ldb_dir, blob_dir):
        msg = normalize(raw)
        if msg is None:
            continue
        if sent_only and not msg["is_sent"]:
            continue
        if from_user and from_user not in msg["sender"].lower():
            continue
        if search and search not in msg["text"].lower():
            continue

        # Dedupe on text alone: the same message appears in several stores, and
        # sender is unreliable here because self-drafts omit imDisplayName.
        key = msg["text"][:DEDUP_PREFIX_LEN]
        if key in seen:
            continue
        seen.add(key)
        messages.append(msg)

    messages.sort(key=lambda m: m["timestamp"])
    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Microsoft Teams messages from an IndexedDB LevelDB cache."
    )
    parser.add_argument("ldb_dir", help="Path to a copy of the IndexedDB .leveldb directory")
    parser.add_argument("--from-user", metavar="NAME",
                        help="Only messages from this display name (default: only your sent messages)")
    parser.add_argument("--search", metavar="WORD",
                        help="Only messages containing this text (case-insensitive)")
    parser.add_argument("--recent", type=int, metavar="N",
                        help="Only the N most recent matches")
    parser.add_argument("--blob-path", metavar="PATH",
                        help="Sibling .blob directory (auto-detected by default)")
    parser.add_argument("--output", "-o", metavar="FILE",
                        help="Write results to FILE instead of stdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ldb_dir = Path(args.ldb_dir).expanduser().resolve()
    if not ldb_dir.is_dir():
        sys.exit(f"Not a directory: {ldb_dir}")

    blob_dir = Path(args.blob_path).expanduser().resolve() if args.blob_path else find_blob_path(ldb_dir)
    if blob_dir:
        print(f"Using blob directory: {blob_dir}", file=sys.stderr)

    print("Scanning IndexedDB message stores...", file=sys.stderr)
    messages = extract(ldb_dir, blob_dir, from_user=args.from_user, search=args.search)
    if args.recent:
        messages = messages[-args.recent:]

    scope = f"from '{args.from_user}'" if args.from_user else "sent"
    if args.search:
        scope += f" matching '{args.search}'"
    words = sum(len(m["text"].split()) for m in messages)
    print(f"Extracted {len(messages)} {scope} messages ({words:,} words)", file=sys.stderr)

    lines = [f"[{m['timestamp']}] {m['text']}\n" for m in messages]
    if args.output:
        Path(args.output).write_text("".join(lines), encoding="utf-8")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.writelines(lines)


if __name__ == "__main__":
    main()
