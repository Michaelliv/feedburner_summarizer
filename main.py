import asyncio
from concurrent.futures import ThreadPoolExecutor

import click

from src.doc_summarizer import DocSummarizer
from src.rss_handler import FeedBurnerHandler, EmptyFeedNameError, EntriesNotFoundError


@click.command()
@click.option("--name", prompt="Enter feed name please")
@click.option("--nouns-enabled/--nouns-disabled", default=False)
@click.option("--iqr-enabled/--iqr-disabled", default=False)
def summarize(name, nouns_enabled, iqr_enabled):
    try:
        click.echo("Initializeing...")

        rss_handler = FeedBurnerHandler()
        summarizer = DocSummarizer(nouns_enabled, iqr_enabled)
        executor = ThreadPoolExecutor()

        feed = rss_handler.fetch_latest(name)
        rss_handler.check_feed_validity(feed)
        rss_data = rss_handler.map_entries(feed.entries)

        loop = asyncio.get_event_loop()

        try:
            for rss in rss_data:
                summarization = loop.run_until_complete(summarizer.summarize(loop, executor, rss))
                click.echo(rss.url)
                click.echo(rss.title)
                click.echo(summarization)
                click.echo()

        except Exception as e:
            click.echo(e)

        finally:
            loop.close()

    except EmptyFeedNameError:
        click.echo("Feed name can't be empty")

    except EntriesNotFoundError:
        click.echo("Feed not found")

    except Exception as e:
        click.echo(e)

    finally:
        return 0


if __name__ == '__main__':
    summarize()
