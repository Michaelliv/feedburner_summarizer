"""Tests for `feedburner_summarizer` package."""


import unittest
from click.testing import CliRunner
from feedparser import FeedParserDict

from feedburner_summarizer import cli
from feedburner_summarizer.rss_handler import FeedBurnerHandler, EntriesNotFoundError, EmptyFeedNameError


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

