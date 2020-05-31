import re
import imaplib
import mimetypes

from io import BytesIO

from email import policy
from email.parser import BytesParser

LIST_PATTERN = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

def open_connection(config):
    print(f"Opening connection to: {config.server} for user: {config.user}")
    connection = imaplib.IMAP4_SSL(config.server)
    connection.login(config.user, config.password)

    return connection

def check_status(connection, config):
    for mname in config.mailboxes:
        check_status_single(connection, mname)

def check_status_single(connection, mname):
    print(f"Checking status on mailbox: {mname}")
    status_typ,status = connection.status(f"\"{mname}\"",'(MESSAGES RECENT UNSEEN)')
    print(f"Status: {status[0].decode('utf-8')[len(mname)+2: -1]}")

def list_mailboxes(connection):
    typ,data = connection.list()
    print(f"Response code: {typ}")
    for line in data:
        match = LIST_PATTERN.match(line.decode('utf-8'))
        flags,delimiter,mname = match.groups()
        mname = mname.strip('"')

        check_status_single(connection, mname)

def mark_read(connection, mbox_messages):
    for mbox in mbox_messages:
        for mid in mbox_messages[mbox]:
            connection.select(f"\"{mbox}\"")

            print(f"Marking message {mid} as read, in mailbox: {mbox}")
            connection.store(mid, '+FLAGS', '(\Seen \Answered)')

def for_message_html(connection, config, fn, max_count=None):
    results = {}
    for mbox in config.mailboxes:
        connection.select(f"\"{mbox}\"", readonly=True)
        stat, raw_id_list = connection.search(None, 'UNSEEN')
        print(f"Raw id list: '{raw_id_list}'")
        msg_ids = list(reversed(list(filter(None, raw_id_list[0].decode('utf-8').split(' ')))))
        if max_count is not None and len(msg_ids) > max_count:
            msg_ids = msg_ids[0:max_count]

        print(f"{stat}: Got {len(msg_ids)} NEW message IDs: {msg_ids}")

        for mid in msg_ids:
            print(f"\nFetching message: {mid}")
            stat, data = connection.fetch(mid, '(RFC822)')
            print(stat)

            if 'OK' != stat:
                print(f"Failed to fetch email {mid}: {stat} {data}")
                continue

            msgdata = None
            for d in data:
                if not isinstance(d[1], int):
                    msgdata = d[1]
                    break

            if msgdata is None:
                print("Can't find valid email message data. Skipping")
                continue

            msg = BytesParser(policy=policy.default).parse(BytesIO(msgdata))

            print(f"Subject: \"{msg['subject']}\"\nFrom: {msg['from']}\nis multipart? {msg.is_multipart()}")

            html = msg.get_body(preferencelist=('html', 'plain')).get_content()
            result = fn(html)
            if result is not None:
                msgs = results.get(result)
                if msgs is None:
                    msgs = {}
                    results[result] = msgs

                box_msgs = msgs.get(mbox)

                if box_msgs is None:
                    box_msgs = []
                    msgs[mbox] = box_msgs

                box_msgs.append(mid)

    return results

def parse_unsub(html):
    regexes = [
        re.compile(r"[Uu]nsubscribe[^<]+<a.+(http[^\"']+)[^>]+>", re.DOTALL),
        re.compile(r"(http[^>'\"]+[Uu]nsubscribe[^\"']+)[^>]+>", re.DOTALL),
        re.compile(r"(http[^\"']+)[^>]+>.*?[Uu]nsubscribe", re.DOTALL),
    ]

    url = None
    for r in regexes:
        print(f"Searching for: {r}")
        smallest = None
        link = None
        for match in re.finditer(r, html):
            if smallest is None or len(smallest) > len(match.group(0)):
                smallest = match.group(0)
                link = match.group(1)

        if link is not None:
            url = link
            break

    print(f"Unsubscribe URL:\n\n    {url}")
    return url

def get_unsubscribe_urls(connection, config, max_count=None):
    return for_message_html(connection, config, parse_unsub, max_count)

def get_text(msg):
    if msg.is_multipart():
        return get_text(msg.get_payload(0))

    return msg.get_payload(None, True);