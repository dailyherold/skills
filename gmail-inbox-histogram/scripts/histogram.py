#!/usr/bin/env python3
"""Gmail sender histogram — top N senders for a Gmail query.

Uses gws CLI for auth and message ID listing, then hits the Gmail batch API
directly for metadata — 100 messages per HTTP round trip instead of one
subprocess per message. Results are cached in SQLite so large queries can
resume if interrupted and subsequent runs are fast.

Default query: is:unread (covers all time, all folders, excludes spam/trash).

Cleanup commands (operate on cached sender data):
  --mark-read PATTERN   mark all messages matching sender pattern as read
  --trash PATTERN       move all messages matching sender pattern to trash
"""

import argparse
import calendar
import email.utils
import fnmatch
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.error
import uuid
from collections import Counter
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# gws helpers
# ---------------------------------------------------------------------------

def gws(*args, account=None):
    """Run a gws command and return stdout as a string."""
    cmd = ['gws']
    if account:
        cmd += ['--account', account]
    cmd += list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f'\ngws error: {detail}', file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def _refresh_access_token(account=None):
    """Exchange a refresh token for an access token via OAuth2."""
    raw = gws('auth', 'export', '--unmasked', account=account)
    creds = json.loads(raw)
    params = json.dumps({
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': creds['refresh_token'],
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=params,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())['access_token']


class TokenManager:
    """Auto-refreshes access token before it expires (~1h).

    Important for overnight runs — 210k messages takes ~70 min.
    """
    TTL = 3500  # refresh 100s before the ~1h expiry

    def __init__(self, account=None):
        self.account = account
        self._token = None
        self._expires_at = 0.0

    def get(self):
        if time.time() >= self._expires_at:
            self._token = _refresh_access_token(self.account)
            self._expires_at = time.time() + self.TTL
        return self._token


def list_message_ids(query, account=None):
    """Return all message IDs matching a Gmail query, auto-paginating."""
    raw = gws(
        'gmail', 'users', 'messages', 'list',
        '--params', json.dumps({'userId': 'me', 'q': query, 'maxResults': 500}),
        '--page-all',
        account=account,
    )
    ids = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            page = json.loads(line)
            for msg in page.get('messages', []):
                ids.append(msg['id'])
        except json.JSONDecodeError:
            pass
    return ids


def list_all_message_ids(base_query, account=None, start_year=2008):
    """List all message IDs by chunking into monthly date windows.

    Works around gws/Gmail pagination limits (~5000) on broad queries like
    is:unread. Each monthly window stays well under the cap.
    """
    seen = {}
    now = datetime.now()
    total_months = (now.year - start_year) * 12 + now.month
    done = 0

    year, month = start_year, 1
    while (year, month) <= (now.year, now.month):
        if month == 12:
            before = f'{year + 1}/01/01'
        else:
            before = f'{year}/{month + 1:02d}/01'
        after = f'{year}/{month:02d}/01'

        chunk_query = f'{base_query} after:{after} before:{before}'
        ids = list_message_ids(chunk_query, account=account)
        for mid in ids:
            seen[mid] = True

        done += 1
        pct = int(done / total_months * 40)
        bar = '█' * pct + '░' * (40 - pct)
        print(f'\r  [{bar}] {year}/{month:02d}  {len(seen)} msgs found',
              end='', flush=True, file=sys.stderr)

        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1

    print(file=sys.stderr)
    return list(seen.keys())


# ---------------------------------------------------------------------------
# SQLite cache
# ---------------------------------------------------------------------------

def open_cache(account):
    """Open (or create) the SQLite sender cache for this account."""
    cache_dir = os.path.expanduser('~/.cache/gmail-histogram')
    os.makedirs(cache_dir, exist_ok=True)
    key = account.replace('@', '_').replace('.', '_') if account else 'default'
    db_path = os.path.join(cache_dir, f'{key}.db')
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS senders (
            msg_id     TEXT PRIMARY KEY,
            sender     TEXT NOT NULL,
            fetched_at INTEGER NOT NULL
        )
    ''')
    conn.commit()
    return conn, db_path


def cache_lookup(conn, msg_ids):
    """Return (cached_dict, uncached_ids).

    Uses chunked IN queries to stay within SQLite's 999-variable limit.
    """
    if not msg_ids:
        return {}, []
    cached = {}
    for i in range(0, len(msg_ids), 900):
        chunk = msg_ids[i:i + 900]
        placeholders = ','.join('?' * len(chunk))
        rows = conn.execute(
            f'SELECT msg_id, sender FROM senders WHERE msg_id IN ({placeholders})',
            chunk,
        ).fetchall()
        for mid, sender in rows:
            cached[mid] = sender
    uncached = [mid for mid in msg_ids if mid not in cached]
    return cached, uncached


def cache_store(conn, senders_dict):
    """Write msg_id → sender pairs to cache."""
    if not senders_dict:
        return
    now = int(time.time())
    conn.executemany(
        'INSERT OR REPLACE INTO senders (msg_id, sender, fetched_at) VALUES (?, ?, ?)',
        [(mid, sender, now) for mid, sender in senders_dict.items()],
    )
    conn.commit()


def cache_senders_matching(conn, pattern):
    """Return list of msg_ids whose sender matches a glob pattern."""
    rows = conn.execute('SELECT msg_id, sender FROM senders').fetchall()
    pat = pattern.lower()
    return [row[0] for row in rows if fnmatch.fnmatch(row[1], pat)]


def cache_delete(conn, msg_ids):
    """Remove msg_ids from cache (e.g. after trashing/marking read)."""
    if not msg_ids:
        return
    for i in range(0, len(msg_ids), 900):
        chunk = msg_ids[i:i + 900]
        placeholders = ','.join('?' * len(chunk))
        conn.execute(f'DELETE FROM senders WHERE msg_id IN ({placeholders})', chunk)
    conn.commit()


# ---------------------------------------------------------------------------
# Batch API fetch
# ---------------------------------------------------------------------------

BATCH_URL = 'https://www.googleapis.com/batch/gmail/v1'
BATCH_SIZE = 100
# Gmail quota: 250 units/sec, messages.get = 5 units → 50 msgs/sec max.
# 100-message batches at 2s delay → exactly 50 msgs/sec, right at ceiling.
BATCH_DELAY = 2.0


def _fmt_eta(seconds):
    if seconds < 60:
        return f'{seconds:.0f}s'
    if seconds < 3600:
        return f'{seconds / 60:.0f}m'
    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    return f'{h}h{m:02d}m'


def _build_batch_body(msg_ids, boundary):
    parts = []
    for mid in msg_ids:
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Type: application/http\r\n\r\n'
            f'GET /gmail/v1/users/me/messages/{mid}'
            f'?format=metadata&metadataHeaders=From HTTP/1.1\r\n\r\n'
        )
    parts.append(f'--{boundary}--\r\n')
    return ''.join(parts).encode()


def _parse_batch_response(body, boundary, chunk_ids):
    """Extract From headers from a multipart batch response.

    Returns (senders_dict, retry_ids).
    """
    senders = {}
    retry_ids = []
    delimiter = f'--{boundary}'.encode()
    parts = body.split(delimiter)

    id_iter = iter(chunk_ids)
    for part in parts[1:]:
        if part.strip() in (b'', b'--', b'--\r\n'):
            continue
        try:
            msg_id = next(id_iter)
        except StopIteration:
            break

        try:
            first_blank = part.find(b'\r\n\r\n')
            if first_blank == -1:
                continue
            http_section = part[first_blank + 4:]
            status_line = http_section.split(b'\r\n')[0].decode('utf-8', errors='replace')
            status = int(status_line.split(' ')[1]) if ' ' in status_line else 0

            if status == 429:
                retry_ids.append(msg_id)
                continue

            second_blank = http_section.find(b'\r\n\r\n')
            if second_blank == -1:
                continue
            payload = json.loads(http_section[second_blank:].strip())
            for h in payload.get('payload', {}).get('headers', []):
                if h.get('name', '').lower() == 'from':
                    _, addr = email.utils.parseaddr(h['value'])
                    senders[msg_id] = addr.lower() if addr else h['value'].lower()
                    break
        except (json.JSONDecodeError, KeyError, ValueError, StopIteration):
            pass

    return senders, retry_ids


def _do_batch(chunk_ids, token):
    """Send one batch request; return (senders_dict, retry_ids)."""
    boundary = uuid.uuid4().hex
    body = _build_batch_body(chunk_ids, boundary)
    req = urllib.request.Request(
        BATCH_URL, data=body,
        headers={'Authorization': f'Bearer {token}',
                 'Content-Type': f'multipart/mixed; boundary={boundary}'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read()
            ct = resp.headers.get('Content-Type', '')
            resp_boundary = next(
                (p.strip()[9:].strip('"') for p in ct.split(';')
                 if p.strip().startswith('boundary=')),
                None,
            )
            if resp_boundary:
                return _parse_batch_response(resp_body, resp_boundary, chunk_ids)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {}, list(chunk_ids)
    return {}, []


def fetch_senders_batch(msg_ids, token_mgr, conn):
    """Fetch From headers for msg_ids, using SQLite cache for known IDs.

    Writes to cache after each batch (incremental → resume on interrupt).
    Returns dict of msg_id → sender.
    """
    cached, uncached = cache_lookup(conn, msg_ids)
    n_cached = len(cached)
    n_to_fetch = len(uncached)
    print(f'  Cache  : {n_cached} hits, {n_to_fetch} to fetch', file=sys.stderr)

    results = dict(cached)
    if not uncached:
        return results

    pending = list(uncached)
    fetched_count = 0
    fetch_start = time.time()
    attempt = 0
    max_attempts = 5

    while pending and attempt < max_attempts:
        if attempt > 0:
            delay = min(2 ** attempt, 60)
            print(f'\n  Retrying {len(pending)} rate-limited messages (wait {delay}s)...',
                  file=sys.stderr)
            time.sleep(delay)

        next_pending = []
        chunks = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]

        for i, chunk in enumerate(chunks):
            senders, retry_ids = _do_batch(chunk, token_mgr.get())
            results.update(senders)
            next_pending.extend(retry_ids)
            cache_store(conn, senders)  # incremental write — resume is free

            fetched_count += len(senders)
            elapsed = time.time() - fetch_start
            rate = fetched_count / elapsed if elapsed > 0 else 0
            remaining = n_to_fetch - fetched_count
            eta = _fmt_eta(remaining / rate) if rate > 0 and remaining > 0 else '—'

            pct = int(fetched_count / n_to_fetch * 40) if n_to_fetch else 40
            bar = '█' * pct + '░' * (40 - pct)
            print(f'\r  [{bar}] {fetched_count}/{n_to_fetch}  ETA {eta}',
                  end='', flush=True, file=sys.stderr)

            if i < len(chunks) - 1:
                time.sleep(BATCH_DELAY)

        pending = next_pending
        attempt += 1

    print(file=sys.stderr)
    if pending:
        print(f'  Warning: {len(pending)} messages could not be fetched after {max_attempts} attempts.',
              file=sys.stderr)
    return results


# ---------------------------------------------------------------------------
# Gmail modify API (cleanup commands)
# ---------------------------------------------------------------------------

MODIFY_URL = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify'
MODIFY_CHUNK = 1000  # API limit per batchModify call


def batch_modify_messages(msg_ids, token_mgr, add_labels=None, remove_labels=None):
    """Apply label changes to a list of messages via Gmail batchModify API.

    Returns number of successfully modified messages.
    """
    total = len(msg_ids)
    modified = 0
    for i in range(0, total, MODIFY_CHUNK):
        chunk = msg_ids[i:i + MODIFY_CHUNK]
        payload = {'ids': chunk}
        if add_labels:
            payload['addLabelIds'] = add_labels
        if remove_labels:
            payload['removeLabelIds'] = remove_labels
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            MODIFY_URL, data=data,
            headers={'Authorization': f'Bearer {token_mgr.get()}',
                     'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            urllib.request.urlopen(req)
            modified += len(chunk)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:300]
            print(f'\n  API error {e.code}: {body}', file=sys.stderr)

        pct = int(modified / total * 40) if total else 40
        bar = '█' * pct + '░' * (40 - pct)
        print(f'\r  [{bar}] {modified}/{total}', end='', flush=True, file=sys.stderr)

        if i + MODIFY_CHUNK < total:
            time.sleep(0.5)

    print(file=sys.stderr)
    return modified


# ---------------------------------------------------------------------------
# Histogram rendering
# ---------------------------------------------------------------------------

def render(counter, top_n):
    items = counter.most_common(top_n)
    if not items:
        print('No data found.')
        return

    max_count = items[0][1]
    max_label = max(len(k) for k, _ in items)
    bar_width = 40
    total = sum(counter.values())

    print(f'\n  Top {len(items)} senders  (of {len(counter)} unique, {total} total messages)\n')
    for sender, count in items:
        filled = int(bar_width * count / max_count)
        bar = '█' * filled + '░' * (bar_width - filled)
        pct = count / total * 100
        print(f'  {sender:<{max_label}}  {bar}  {count:>5}  ({pct:.1f}%)')
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Gmail sender histogram. Default query: is:unread (all time).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
Cleanup commands (use after building cache with a fetch run):
  --mark-read PATTERN   Mark all cached messages matching sender as read.
                        Supports globs: "*@github.com", "noreply*"
  --trash PATTERN       Move all cached messages matching sender to trash.
                        Same glob syntax as --mark-read.

Examples:
  # First run (overnight): fetch all unread
  python3 histogram.py

  # Show histogram from cache (fast)
  python3 histogram.py --no-fetch

  # Mark all GitHub notifications as read
  python3 histogram.py --mark-read "*@github.com"

  # Trash a specific sender
  python3 histogram.py --trash "newsletter@example.com"
''',
    )
    parser.add_argument('--months', type=int, default=None,
                        help='Lookback in months (overrides default is:unread query)')
    parser.add_argument('--top', type=int, default=20,
                        help='Number of top senders to show (default: 20)')
    parser.add_argument('--query', default=None,
                        help='Override the Gmail search query entirely')
    parser.add_argument('--account',
                        help='gws account to use (omit for default)')
    parser.add_argument('--no-fetch', action='store_true',
                        help='Render from cache only — no API calls')
    parser.add_argument('--refresh', action='store_true',
                        help='Clear cache and re-fetch everything')
    parser.add_argument('--mark-read', metavar='PATTERN',
                        help='Mark all cached messages from matching sender as read')
    parser.add_argument('--trash', metavar='PATTERN',
                        help='Move all cached messages from matching sender to trash')
    parser.add_argument('--start-year', type=int, default=2008,
                        help='Earliest year to include in chunked listing (default: 2008)')
    parser.add_argument('--yes', action='store_true',
                        help='Skip confirmation prompts for --mark-read and --trash')
    args = parser.parse_args()

    conn, db_path = open_cache(args.account)
    print(f'  Cache  : {db_path}', file=sys.stderr)

    # --- Cleanup commands ---

    if args.mark_read:
        msg_ids = cache_senders_matching(conn, args.mark_read)
        print(f'  Found  : {len(msg_ids)} cached messages matching "{args.mark_read}"',
              file=sys.stderr)
        if not msg_ids:
            print('  Nothing to do. Run a fetch first if cache is empty.', file=sys.stderr)
            return
        if not args.yes:
            answer = input(f'  Mark {len(msg_ids)} messages as read? [y/N] ').strip().lower()
            if answer != 'y':
                print('  Aborted.', file=sys.stderr)
                return
        print('  Marking as read (removing UNREAD label)...', file=sys.stderr)
        token_mgr = TokenManager(account=args.account)
        n = batch_modify_messages(msg_ids, token_mgr, remove_labels=['UNREAD'])
        cache_delete(conn, msg_ids)
        print(f'  Done: {n}/{len(msg_ids)} messages marked as read, removed from cache.',
              file=sys.stderr)
        return

    if args.trash:
        msg_ids = cache_senders_matching(conn, args.trash)
        print(f'  Found  : {len(msg_ids)} cached messages matching "{args.trash}"',
              file=sys.stderr)
        if not msg_ids:
            print('  Nothing to do. Run a fetch first if cache is empty.', file=sys.stderr)
            return
        if not args.yes:
            answer = input(f'  Move {len(msg_ids)} messages to trash? [y/N] ').strip().lower()
            if answer != 'y':
                print('  Aborted.', file=sys.stderr)
                return
        print('  Moving to trash...', file=sys.stderr)
        token_mgr = TokenManager(account=args.account)
        n = batch_modify_messages(msg_ids, token_mgr,
                                  add_labels=['TRASH'],
                                  remove_labels=['INBOX', 'UNREAD'])
        cache_delete(conn, msg_ids)
        print(f'  Done: {n}/{len(msg_ids)} messages trashed, removed from cache.',
              file=sys.stderr)
        return

    # --- Cache management ---

    if args.refresh:
        conn.execute('DELETE FROM senders')
        conn.commit()
        print('  Cache cleared.', file=sys.stderr)

    if args.no_fetch:
        rows = conn.execute('SELECT sender FROM senders').fetchall()
        if not rows:
            print('\n  Cache is empty. Run without --no-fetch first.\n')
            return
        render(Counter(r[0] for r in rows), args.top)
        return

    # --- Histogram fetch + render ---

    if args.query:
        query = args.query
    elif args.months:
        since = datetime.now() - timedelta(days=args.months * 30)
        query = f'after:{since.strftime("%Y/%m/%d")}'
    else:
        query = 'is:unread'

    print(f'  Query  : {query}', file=sys.stderr)

    print('  Getting access token...', file=sys.stderr)
    token_mgr = TokenManager(account=args.account)
    token_mgr.get()  # eager fetch so auth errors surface immediately

    print('  Listing messages (monthly chunks to bypass 5k cap)...', file=sys.stderr)
    msg_ids = list_all_message_ids(query, account=args.account, start_year=args.start_year)
    print(f'  Found  : {len(msg_ids)} messages', file=sys.stderr)

    if not msg_ids:
        print('\n  No messages matched the query.\n')
        return

    n_batches = (len(msg_ids) + BATCH_SIZE - 1) // BATCH_SIZE
    est_mins = n_batches * BATCH_DELAY / 60
    print(f'  Fetching metadata ({n_batches} batches, ~{est_mins:.0f} min if all uncached)...',
          file=sys.stderr)

    results = fetch_senders_batch(msg_ids, token_mgr, conn)

    senders_list = [results.get(mid, '<unknown>') for mid in msg_ids]
    render(Counter(senders_list), args.top)


if __name__ == '__main__':
    main()
