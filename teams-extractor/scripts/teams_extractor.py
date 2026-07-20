#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "python-snappy>=0.7",
# ]
# requires-python = ">=3.11"
# ///
"""
Extract Microsoft Teams messages from a local IndexedDB LevelDB cache.

Bypasses LevelDB's DB::Open entirely by reading SSTable (.ldb) and WAL (.log)
files directly. This sidesteps the idb_cmp1 custom comparator validation that
blocks plyvel/leveldown.

Usage:
  python teams_extractor.py <path/to/indexeddb.leveldb> [--output FILE]
                            [--from-user DISPLAY_NAME]
                            [--search KEYWORD]

The LevelDB path for Chromium Teams (web) is typically:
  ~/.config/chromium/Default/IndexedDB/
    https_teams.cloud.microsoft_0.indexeddb.leveldb/

Because Teams holds a write lock, copy the directory first:
  cp -r "<leveldb-path>" /tmp/teams_leveldb_copy

Output format: one line per message: [YYYY-MM-DDTHH:MM:SS] message text
Readable messages only (>70% printable ASCII, deduped).

Key differences from sent-only mode:
  --from-user NAME  filters to messages FROM a specific display name
  --search KEYWORD  filters to messages containing a keyword (case-insensitive)
  Default (no flags) extracts only messages sent by the current user.
"""

import sys
import struct
import re
import argparse
from pathlib import Path

try:
    import snappy
except ImportError:
    print("need snappy: uv add python-snappy", file=sys.stderr)
    sys.exit(1)

BLOCK_TRAILER_SIZE = 5
MAGIC = b'\x57\xfb\x80\x8b\x24\x75\x47\xdb'
FOOTER_SIZE = 48

def decode_varint(data, pos):
    result, shift = 0, 0
    while pos < len(data):
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return result, pos

def decode_block_handle(data, pos):
    o, pos = decode_varint(data, pos)
    s, pos = decode_varint(data, pos)
    return o, s, pos

def read_block(f, offset, size):
    f.seek(offset)
    raw = f.read(size + BLOCK_TRAILER_SIZE)
    if len(raw) < BLOCK_TRAILER_SIZE: return None
    ct = raw[size]; bd = raw[:size]
    if ct == 0: return bd
    if ct == 1:
        try: return snappy.decompress(bd)
        except: return None
    return None

def parse_block_entries(block_data):
    if len(block_data) < 4: return []
    nr = struct.unpack_from('<I', block_data, len(block_data)-4)[0]
    if nr == 0 or nr > 100000: return []
    ro = len(block_data) - 4 - nr * 4
    if ro < 0: return []
    entries, pos, ck = [], 0, b''
    while pos < ro:
        try:
            sl, pos = decode_varint(block_data, pos)
            ul, pos = decode_varint(block_data, pos)
            vl, pos = decode_varint(block_data, pos)
        except: break
        if pos + ul + vl > ro: break
        ks = block_data[pos:pos+ul]; pos += ul
        v  = block_data[pos:pos+vl]; pos += vl
        ck = ck[:sl] + ks
        entries.append((ck, v))
    return entries

def iter_sstable(filepath):
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, 2); fsz = f.tell()
            if fsz < FOOTER_SIZE: return
            f.seek(fsz - FOOTER_SIZE)
            footer = f.read(FOOTER_SIZE)
            if footer[40:48] != MAGIC: return
            pos = 0
            _, pos = decode_varint(footer, pos)
            _, pos = decode_varint(footer, pos)
            io_, pos = decode_varint(footer, pos)
            is_, pos = decode_varint(footer, pos)
            idx = read_block(f, io_, is_)
            if idx is None: return
            for _, hb in parse_block_entries(idx):
                if not hb: continue
                try: do, ds, _ = decode_block_handle(hb, 0)
                except: continue
                bd = read_block(f, do, ds)
                if bd is None: continue
                yield from parse_block_entries(bd)
    except: pass

def is_sent_by_me(value: bytes) -> bool:
    """Check if isSentByCurrentUser = true in this V8-serialized value."""
    idx = value.find(b'isSentByCurrentUser')
    if idx < 0:
        return False
    after = value[idx + len(b'isSentByCurrentUser'):]
    # V8 boolean tags: 'T' (0x54) = true, 'F' (0x46) = false. A length-prefix
    # sometimes separates the key from the tag, so scan a short window rather
    # than assuming a fixed offset.
    for byte in after[:8]:
        if byte == 0x54:  # 'T' = true
            return True
        if byte == 0x46:  # 'F' = false
            return False
    return False

def extract_content_field(value: bytes) -> str | None:
    """
    Extract the 'content' field from a V8-serialized Teams message.
    The content field contains the HTML message body.

    Fallback for extract_html_content(): used when that function's
    blockquote-aware scan doesn't find a match. V8 strings are tagged
    values: 0x22 (one-byte string) + varint length + bytes, or 0x63
    (two-byte string) + varint length + utf16-le bytes. The value tag
    normally follows the 'content"' key immediately.
    """
    content_idx = value.find(b'content"')
    if content_idx < 0:
        return None

    after_content = value[content_idx + len(b'content"'):]
    if len(after_content) < 3:
        return None

    # Scan a short window for the V8 string tag and decode accordingly
    for i, b in enumerate(after_content[:20]):
        if b == 0x22:  # V8 one-byte string tag
            # Next byte(s) are the length
            length, new_pos = decode_varint(after_content, i + 1)
            if 0 < length < 100000 and new_pos + length <= len(after_content):
                raw_str = after_content[new_pos:new_pos + length]
                try:
                    text = raw_str.decode('utf-8', errors='replace')
                    return text
                except:
                    pass
        elif b == 0x63:  # V8 two-byte string tag
            length, new_pos = decode_varint(after_content, i + 1)
            if 0 < length < 100000 and new_pos + length * 2 <= len(after_content):
                raw_str = after_content[new_pos:new_pos + length * 2]
                try:
                    text = raw_str.decode('utf-16-le', errors='replace')
                    return text
                except:
                    pass

    # Fallback: grab ASCII run starting from content"
    m = re.search(rb'content"(.{0,20}?)(<[a-zA-Z]|[A-Za-z]{3,})', value[content_idx:])
    if m:
        start = content_idx + m.start(2)
        # Extract until we hit a null byte or V8 key separator
        chunk = value[start:start+5000]
        text = chunk.decode('utf-8', errors='replace')
        # Cut off at first null or control char cluster
        text = re.split(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text)[0]
        return text if len(text) > 5 else None

    return None

def clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_timestamp(value: bytes) -> str | None:
    """Extract timestamp from message value. Tries composetime ISO string first,
    then falls back to 13-digit Unix-ms integers embedded in the value."""
    # composetime ISO string (works for older/compacted .ldb entries)
    idx = value.find(b'composetime"')
    if idx >= 0:
        after = value[idx + len(b'composetime"'):]
        m = re.search(rb'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', after[:50])
        if m:
            return m.group(1).decode('ascii')
    # Fallback: 13-digit Unix-ms timestamp (works for WAL entries and received msgs)
    matches = re.findall(rb'\b(17\d{11})\b', value)
    if matches:
        try:
            from datetime import datetime, timezone
            dt = datetime.fromtimestamp(int(matches[0]) / 1000, tz=timezone.utc)
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        except Exception:
            pass
    return None


def extract_html_content(raw_bytes: bytes) -> str | None:
    """Extract the full HTML content field, including blockquote bodies.
    Teams stores the outer message wrapper and blockquote content in the same
    byte sequence but the blockquote inner text may follow a V8 object boundary.
    We scan for the content" marker and grab everything through </blockquote>
    or the contentHash" terminator, whichever comes first."""
    idx = raw_bytes.find(b'content"')
    if idx < 0:
        return None
    # Skip the V8 length/type byte(s) after content"
    start = idx + len(b'content"')
    # Scan forward up to 8 bytes for the start of HTML
    for offset in range(8):
        if start + offset >= len(raw_bytes):
            break
        if raw_bytes[start + offset:start + offset + 2] in (b'<p', b'<b', b'<s', b'<u', b'<d', b'<h', b'<i', b'<o'):
            start = start + offset
            break
    # Find end: contentHash" or isSentByCurrentUser or 20000 chars
    end_markers = [b'contentHash"', b'isSentByCurrentUser']
    end = len(raw_bytes)
    for marker in end_markers:
        pos = raw_bytes.find(marker, start)
        if pos > start:
            end = min(end, pos)
    if end <= start:
        return None
    chunk = raw_bytes[start:end]
    try:
        return chunk.decode('utf-8', errors='replace')
    except Exception:
        return None


def iter_wal(filepath: str):
    """Iterate over value blobs in a LevelDB WAL (.log) file.
    WAL format: sequence of 32KB blocks, each containing records.
    Record header: checksum(4) + length(2) + type(1). Types: 1=full, 2=first, 3=middle, 4=last.
    We use a simpler approach: scan for V8 object boundaries by looking for
    known Teams field markers rather than parsing the full WAL structure."""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
    except Exception:
        return

    # Find all positions of the creator" field (marks start of a message object)
    # and extract the value blob from there to the next high-level boundary
    creator_marker = b'creator",'
    pos = 0
    while True:
        idx = raw.find(creator_marker, pos)
        if idx < 0:
            break
        # Grab up to 8000 bytes — enough for any single Teams message
        blob = raw[idx:idx + 8000]
        # Find end of this message object: next creator" or end of reasonable scope
        next_creator = raw.find(creator_marker, idx + 100)
        if next_creator > idx:
            blob = raw[idx:min(next_creator, idx + 8000)]
        yield b'', blob
        pos = idx + 50

def is_readable(text: str, threshold: float = 0.70) -> bool:
    """True if >threshold of characters are printable ASCII."""
    if not text:
        return False
    printable = sum(1 for c in text if ord(c) < 128 and c.isprintable())
    return printable / len(text) >= threshold


def _extract_from_blob(value: bytes, filter_sender_id: bytes | None,
                       sent_only: bool, search: str | None,
                       seen: set, results: list, source: str) -> int:
    """Shared extraction logic for both .ldb and .log blobs."""
    if not value:
        return 0

    # Sender filter
    if sent_only and not is_sent_by_me(value):
        return 0
    if filter_sender_id and filter_sender_id not in value:
        return 0

    # Use enhanced HTML extractor that handles blockquotes in WAL
    content = extract_html_content(value)
    if not content:
        content = extract_content_field(value)
    if not content:
        return 0

    text = clean_html(content)
    if len(text) < 10 or not is_readable(text):
        return 0

    if search and search.lower() not in text.lower():
        return 0

    ts = extract_timestamp(value)
    dedup_key = text[:150]
    if dedup_key in seen:
        return 0
    seen.add(dedup_key)
    results.append({'timestamp': ts or 'unknown', 'text': text, 'source': source})
    return 1


def extract_all(ldb_dir: Path, from_user: str | None = None,
                search: str | None = None) -> list[dict]:
    """Extract messages from an IndexedDB LevelDB directory.

    Args:
        ldb_dir:   Path to the copied .leveldb directory.
        from_user: If set, return only messages FROM this display name
                   (e.g. 'Jane Doe'). Disables sent-only filter.
        search:    If set, return only messages containing this keyword.
    """
    sent_only = from_user is None
    filter_sender_id = None
    if from_user:
        # Match on the display name string as it appears in the serialized blob
        filter_sender_id = from_user.encode('utf-8')

    ldb_files = sorted(ldb_dir.glob('*.ldb'))
    wal_files = sorted(ldb_dir.glob('*.log'))
    print(f"Scanning {len(ldb_files)} .ldb + {len(wal_files)} .log files...", file=sys.stderr)

    messages = []
    seen_content = set()

    for ldb_file in ldb_files:
        file_msgs = 0
        for _key, value in iter_sstable(str(ldb_file)):
            file_msgs += _extract_from_blob(
                value, filter_sender_id, sent_only, search,
                seen_content, messages, ldb_file.name
            )
        if file_msgs:
            print(f"  {ldb_file.name}: {file_msgs} messages", file=sys.stderr)

    for wal_file in wal_files:
        file_msgs = 0
        for _key, value in iter_wal(str(wal_file)):
            file_msgs += _extract_from_blob(
                value, filter_sender_id, sent_only, search,
                seen_content, messages, wal_file.name
            )
        if file_msgs:
            print(f"  {wal_file.name}: {file_msgs} messages", file=sys.stderr)

    messages.sort(key=lambda m: m['timestamp'])
    return messages


def main():
    parser = argparse.ArgumentParser(description="Extract Teams messages from LevelDB cache")
    parser.add_argument("ldb_dir", help="Path to IndexedDB .leveldb directory (copy, not live)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--from-user", default=None,
                        help="Filter to messages FROM this display name (e.g. 'Jane Doe')")
    parser.add_argument("--search", default=None,
                        help="Filter to messages containing this keyword")
    parser.add_argument("--recent", type=int, default=None,
                        help="Show only the N most recent messages")
    args = parser.parse_args()

    ldb_dir = Path(args.ldb_dir).expanduser().resolve()
    if not ldb_dir.is_dir():
        print(f"Error: not a directory: {ldb_dir}", file=sys.stderr)
        sys.exit(1)

    messages = extract_all(ldb_dir, from_user=args.from_user, search=args.search)

    if args.recent:
        messages = messages[-args.recent:]

    total_words = sum(len(m['text'].split()) for m in messages)
    label = f"from '{args.from_user}'" if args.from_user else "sent"
    if args.search:
        label += f" matching '{args.search}'"
    print(f"\nExtracted {len(messages)} {label} messages ({total_words:,} words)", file=sys.stderr)

    if args.output:
        out = open(args.output, 'w', encoding='utf-8')
    else:
        out = sys.stdout

    for m in messages:
        ts = m['timestamp']
        text = m['text'].replace('\n', ' ')
        out.write(f"[{ts}] {text}\n")

    if args.output:
        out.close()
        print(f"Written to {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
