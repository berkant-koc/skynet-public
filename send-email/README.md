# send-email

Thin shell wrapper around [msmtp](https://marlam.de/msmtp/) for cron /
systemd-timer use.

Removes the boilerplate of authoring a `From:` / `Subject:` /
`Content-Type:` header block by hand every time a script wants to fire
a mail. One line. Configurable via three environment variables.

## Quickstart

```bash
# 1. install msmtp
sudo apt install msmtp msmtp-mta

# 2. configure ~/.msmtprc (chmod 600)
cat > ~/.msmtprc <<'EOF'
defaults
auth on
tls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile ~/.msmtp.log

account home
host smtp.example.com
port 465
user you@example.com
from you@example.com
passwordeval "cat ~/.smtp-password"

account default : home
EOF
chmod 600 ~/.msmtprc

# 3. drop SMTP password (chmod 600!)
echo "your-pass" > ~/.smtp-password
chmod 600 ~/.smtp-password

# 4. install send_email somewhere on PATH
install -m 755 send_email ~/.local/bin/send_email

# 5. fire
export SEND_EMAIL_FROM=you@example.com
send_email someone@example.com "Subject line" "Body text"
echo "Body from stdin" | send_email someone@example.com "Subject line"
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `SEND_EMAIL_FROM` | *(required)* | Sender address, must match an msmtp account |
| `SEND_EMAIL_ACCOUNT` | `default` | msmtp account name from `~/.msmtprc` |
| `SEND_EMAIL_LOG` | `~/.send-email.log` | Append-only dispatch log |

## systemd-timer example

`~/.config/systemd/user/morning-report.service`:

```ini
[Unit]
Description=Daily morning status mail

[Service]
Type=oneshot
Environment="SEND_EMAIL_FROM=you@example.com"
Environment="SEND_EMAIL_ACCOUNT=home"
ExecStart=/bin/bash -c 'uptime | %h/.local/bin/send_email you@example.com "morning"'
```

## Exit codes

| Code | Reason |
|---|---|
| 0 | Mail sent |
| 1 | Bad usage |
| 2 | `msmtp` not installed |
| 3 | `~/.msmtprc` missing |
| 4 | `SEND_EMAIL_FROM` not set |
| 5 | msmtp dispatch failed (check stderr) |

## Why not just `mail` or `sendmail`?

- `mail` / `mailx` headers are hostile to script. Three lines of `From:` /
  `Subject:` / `Content-Type:` boilerplate every time.
- `sendmail` direct invocation hides the SMTP account selection.
- `msmtp` is small (~150KB), supports per-account configs cleanly, and
  this wrapper keeps the call-site to one line.

## License

MIT. See repository `LICENSE`.
