import click
import unsubmail.config as config
import unsubmail.imap as imap
import unsubmail.http as http

@click.command()
@click.option('--config-file', '-c', help='Alternative config YAML')
@click.option('--max-count', '-C', help='Maximum messages to process')
def unsubscribe(config_file=None, max_count=None):
    cfg = config.load(config_file)
    with imap.open_connection(cfg) as conn:
        # imap.list_mailboxes(conn)
        imap.check_status(conn, cfg)

        max_to_process = None
        if max_count is not None:
            max_to_process = int(max_count)

        urls = imap.get_unsubscribe_urls(conn, cfg, max_to_process)
        # url_listing = "\n- ".join(urls)
        print(f"\n\nFound {len(urls)} unsubscribe URLs")

        for url in urls:
            messages_containing = urls[url]
            print(f"Processing...\n\nURL: {url}\nFor Messages: {messages_containing}\n\n")

            if http.process_unsub(url) is True:
                print(f"Unsubscribe apparently successful for: {messages_containing}")
                imap.mark_read(conn, messages_containing)
            else:
                print(f"Unsubscribe failed for: {messages_containing}")


