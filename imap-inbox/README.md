# imap-inbox

A read-only CLI that prints the most recent N mails per configured
IMAP account: one line per mail, `Date | From | Subject`. Nothing is
marked as read. Python stdlib only, no third-party deps.

## Why

When several accounts forward into a single mailbox, you sometimes
want a glance at what's actually arriving on the source side without
opening a mail client. This is `mailx` for the "one-line-per-mail
overview across N accounts" case.

## Install

Drop `imap-inbox.py` somewhere on `$PATH`:

```bash
chmod +x imap-inbox.py
ln -s "$PWD/imap-inbox.py" ~/.local/bin/imap-inbox
```

## Configure

Copy the example, edit, and store passwords in 0600 files:

```bash
mkdir -p ~/.config/imap-inbox
cp accounts.example.json ~/.config/imap-inbox/accounts.json
$EDITOR ~/.config/imap-inbox/accounts.json

# one file per account, password on a single line, mode 600
install -m 600 /dev/null ~/.config/imap-inbox/.primary.pw
$EDITOR ~/.config/imap-inbox/.primary.pw
```

A different config path can be set via `$IMAP_INBOX_CONFIG` or
`--config`.

## Usage

```bash
imap-inbox                       # all accounts, 30 most recent each
imap-inbox --limit 50            # 50 most recent each
imap-inbox --account primary     # just one
imap-inbox --config /etc/imap-inbox/accounts.json
```

Sample output:

```
=== Primary inbox  <alice@example.com> ===
  Total mails in INBOX: 412
  2026-05-14 12:49 | OpenDMARC Filter <opendmarc@...>             | DMARC authentication failure report
  2026-05-14 11:03 | GitHub <noreply@github.com>                  | Re: [example/repo] PR #42 review feedback
  ...
```

## What it does NOT do

- Does not modify any IMAP flags (uses `BODY.PEEK`, opens `INBOX` in
  read-only mode).
- Does not download attachments or message bodies — only the three
  headers `From`, `Subject`, `Date`.
- Does not store mail or state locally.
- Does not connect anywhere outside the configured `host:port`.
- Does not write to the config file or password files.

## License

MIT, see top-level `LICENSE`.
