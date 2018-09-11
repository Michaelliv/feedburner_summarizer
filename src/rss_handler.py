"""RSS handler module"""
from typing import AnyStr, List

from feedparser import parse


class EmptyFeedNameError(Exception):
    pass


class EntriesNotFoundError(Exception):
    pass


class RSSData:
    def __init__(self, url: str, title: str, content: str):
        self.url = url
        self.title = title
        self.content = content


class FeedBurnerHandler:

    @staticmethod
    def fetch_latest(feed_name: AnyStr):
        if not feed_name:
            raise EmptyFeedNameError

        return parse("http://feeds.feedburner.com/{}".format(feed_name))

    @staticmethod
    def check_feed_validity(feed):
        if feed.status == 404:
            raise EntriesNotFoundError

    @staticmethod
    def map_entries(entries: List) -> List[RSSData]:
        return [RSSData(entry.link, entry.title, entry.summary) for entry in entries]
