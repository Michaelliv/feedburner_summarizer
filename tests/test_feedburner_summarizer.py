"""Tests for `feedburner_summarizer` package."""

import asyncio
import unittest

from click.testing import CliRunner
from feedparser import FeedParserDict

from feedburner_summarizer import cli
from feedburner_summarizer.doc_summarizer import DocSummarizer
from feedburner_summarizer.rss_handler import FeedBurnerHandler, EntriesNotFoundError, EmptyFeedNameError, RSSData


class TestFeedBurnerSummarizer(unittest.TestCase):
    """Tests for `feedburner_summarizer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'feedburner_summarizer.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_rss_handler_fetch_latest(self):
        with self.assertRaises(EmptyFeedNameError):
            rss = FeedBurnerHandler()
            rss.fetch_latest("")

    def test_rss_handler_check_validity(self):
        with self.assertRaises(EntriesNotFoundError):
            rss = FeedBurnerHandler()
            rss.check_feed_validity(rss.fetch_latest("TechCrun"))

    def test_rss_handler_map_entries(self):
        rss = FeedBurnerHandler()

        mock_rss = FeedParserDict({"link": "url1", "title": "title1", "summary": "summary1"})

        rss_data = rss.map_entries([mock_rss])

        assert rss_data[0].url == mock_rss.link
        assert rss_data[0].title == mock_rss.title
        assert rss_data[0].content == mock_rss.summary

    def test_rss_handler_full_run(self):
        rss = FeedBurnerHandler()
        feed = rss.fetch_latest("TechCrunch")
        rss.check_feed_validity(feed)
        entries = rss.map_entries(feed.entries)
        assert len(entries) > 0

    def test_doc_summarizer_init(self):
        DocSummarizer()

    def test_doc_summarizer_load_en_most_commons_file(self):
        summarizer = DocSummarizer()
        assert len(summarizer.load_en_most_common_file()) == 1000

    def test_doc_summarizer_cleanup_most_common(self):
        summarizer = DocSummarizer()

        source_text = ["the", "of", "with", "what", "not_a_common_word"]
        expected_text = ["not_a_common_word"]

        clean_text = summarizer.cleanup_en_most_common_words(source_text)

        assert clean_text == expected_text

    def test_doc_summarizer_summarize(self):

        entry_title = """Samsung launches an LTE-enabled Tile competitor"""
        entry_content = """Samsung, naturally, would never be content to launch a regular old Tile competitor. 
        The company just doesn’t roll like that. While the basic foundation of the SmartThings Tracker is similar 
        to what Tile and a number of other startups offer, Samsung’s packed all it can into the product. The device 
        tracker utilizes a combination of GPS to help locate lost products. The addition of LTE-M, meanwhile, means 
        things like lost keys, backpacks and other belongings can be found through a much broader range of settings 
        than standard Bluetooth-enabled products. That means, among other things, that tracking is easier to pinpoint 
        indoors and below ground. The device is compatible with Samsung’s existing SmartThings app (kind of a catchall 
        for all things Samsung IoT) for Android and iOS, offering, among other things, real-time tracking. There’s also 
        a geofencing setting that lets the Tracker double as an arrival sensor to help trigger different smart home 
        functionality when the wearer gets home. When attached to something like a dog collar, meanwhile, it will set a 
        notification when a pet has crossed a certain barrier. The product launches September 14 as an AT&T exclusive, 
        with a Verizon version launching later in the year. It’s not exactly cheap, with a $99 price tag — though that 
        includes 12 free months of LTE-M service. After that, it will run $5 a month — so that will add up pretty 
        quickly.
        """

        rss_data = RSSData("", entry_title, entry_content)

        summarizer = DocSummarizer()
        loop = asyncio.get_event_loop()

        try:
            summarization = loop.run_until_complete(summarizer.summarize(rss_data))
            print(summarization)
        finally:
            loop.close()
