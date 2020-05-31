# Unsubscriber for IMAP

This application goes through a nominated mailbox on an IMAP server, looking for emails with unsubscribe links. Then, it does its best to actually unsubscribe you from those emails.

## Configuration

By default, this will live in `$HOME/.config/unsubmail/config.yaml`. The configuration should look like this:

```
server: imap.myhost.com
user: me@nobody.com
password: pass:my-secret-password-key
mailboxes:
  - INBOX.COMMERCIAL
```

**NOTE:** It's possible to use the linux `pass` command to store the password. If you set the password with the format `pass:some-key`, the application will use the `pass some-key` command to retrieve it. Otherwise, you're free to use a plaintext password here.


## Running

`unsubmail [-c /path/to/alt/config] [-C nn]`
