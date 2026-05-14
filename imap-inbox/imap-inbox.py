#!/usr/bin/env python3
"""Multi-account IMAP inbox overview — read-only.

Reads account credentials from a JSON config file and prints the most
recent N mails per account (Date / From / Subject). Does not mark
anything as read.

Config format (see accounts.example.json):

    {
      "accounts": [
        {
          "key": "primary",
          "label": "Primary inbox",
          "host": "imap.example.com",
          "port": 993,
          "user": "alice@example.com",
          "password_file": "~/.config/imap-inbox/.primary.pw"
        }
      ]
    }

The password file should be chmod 600 and contain the password on one
line.

Usage:
    imap-inbox.py
    imap-inbox.py --limit 50
    imap-inbox.py --account primary
    imap-inbox.py --config /etc/imap-inbox/accounts.json
"""
from __future__ import annotations

import argparse
import email
import email.utils
import imaplib
import json
import os
import sys
from dataclasses import dataclass
from email.header import decode_header, make_header
from pathlib import Path


@dataclass
class Account:
    key: str
    label: str
    host: str
    port: int
    user: str
    password_file: Path


def load_accounts(config_path: Path) -> list[Account]:
    raw = json.loads(config_path.read_text())
    out: list[Account] = []
    for a in raw.get("accounts", []):
        pwf = os.path.expanduser(os.path.expandvars(a["password_file"]))
        out.append(
            Account(
                key=a["key"],
                label=a["label"],
                host=a["host"],
                port=int(a.get("port", 993)),
                user=a["user"],
                password_file=Path(pwf),
            )
        )
    return out


def decode_h(value: str) -> str:
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def shorten(s: str, n: int) -> str:
    s = s.replace("\n", " ").replace("\r", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "..."


def read_account(acc: Account, limit: int) -> None:
    print(f"\n=== {acc.label}  <{acc.user}> ===")
    try:
        pw = acc.password_file.read_text().strip()
    except OSError as e:
        print(f"  PASSWORD-FILE-ERROR: {e}")
        return

    try:
        imap = imaplib.IMAP4_SSL(acc.host, acc.port)
    except OSError as e:
        print(f"  IMAP-CONNECT-ERROR ({acc.host}:{acc.port}): {e}")
        return

    try:
        try:
            imap.login(acc.user, pw)
        except imaplib.IMAP4.error as e:
            print(f"  LOGIN-ERROR: {e}")
            return

        typ, data = imap.select("INBOX", readonly=True)
        if typ != "OK":
            print(f"  SELECT-ERROR: {typ} {data}")
            return
        n_total = int(data[0]) if data and data[0] else 0
        print(f"  Total mails in INBOX: {n_total}")

        if n_total == 0:
            print("  (empty)")
            return

        typ, data = imap.search(None, "ALL")
        if typ != "OK":
            print(f"  SEARCH-ERROR: {typ}")
            return
        ids = data[0].split()
        last_ids = ids[-limit:]
        for mid in reversed(last_ids):  # newest first
            typ, msg_data = imap.fetch(
                mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
            )
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            date_str = msg.get("Date", "")
            try:
                dt = email.utils.parsedate_to_datetime(date_str)
                date_fmt = (
                    dt.strftime("%Y-%m-%d %H:%M") if dt else (date_str or "")[:16]
                )
            except Exception:
                date_fmt = (date_str or "")[:16]
            frm = shorten(decode_h(msg.get("From", "")), 44)
            subj = shorten(decode_h(msg.get("Subject", "")), 70)
            print(f"  {date_fmt:<16} | {frm:<44} | {subj}")
    finally:
        try:
            imap.close()
        except Exception:
            pass
        try:
            imap.logout()
        except Exception:
            pass


def main() -> None:
    default_cfg = os.environ.get(
        "IMAP_INBOX_CONFIG", "~/.config/imap-inbox/accounts.json"
    )
    ap = argparse.ArgumentParser(
        description="Print recent mails (Date/From/Subject) per configured IMAP account, read-only.",
    )
    ap.add_argument(
        "--config",
        type=lambda p: Path(os.path.expanduser(p)),
        default=Path(os.path.expanduser(default_cfg)),
        help="path to accounts.json (default: $IMAP_INBOX_CONFIG or ~/.config/imap-inbox/accounts.json)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=30,
        help="how many recent mails per account (default: 30)",
    )
    ap.add_argument(
        "--account",
        default="all",
        help="key of a single account to read, or 'all' (default: all)",
    )
    args = ap.parse_args()

    if not args.config.is_file():
        print(f"ERROR: config file not found at {args.config}", file=sys.stderr)
        print(
            "       copy accounts.example.json, edit, and place it there,",
            file=sys.stderr,
        )
        print("       or set IMAP_INBOX_CONFIG.", file=sys.stderr)
        sys.exit(2)

    accounts = load_accounts(args.config)
    if not accounts:
        print("ERROR: no accounts defined in config", file=sys.stderr)
        sys.exit(2)

    if args.account == "all":
        targets = accounts
    else:
        targets = [a for a in accounts if a.key == args.account]
        if not targets:
            valid = ", ".join(a.key for a in accounts) or "(none)"
            print(
                f"ERROR: account '{args.account}' not in config. Known: {valid}",
                file=sys.stderr,
            )
            sys.exit(2)

    for acc in targets:
        read_account(acc, limit=args.limit)


if __name__ == "__main__":
    main()
