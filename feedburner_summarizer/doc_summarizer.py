import asyncio
from collections import ChainMap
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import List

import numpy as np
import spacy
import wikipedia

from feedburner_summarizer.definitions import EN_MOST_COMMON_FILE
from feedburner_summarizer.rss_handler import RSSData


class DocSummarizer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.loop = asyncio.get_event_loop()
        self.en_most_common = set(self.load_en_most_common_file())
        self.nlp = spacy.load('en_core_web_sm')

    def annotate(self, text):
        return self.nlp(text)

    def cleanup(self, annotated_tokens: List):
        return [token.lower_ for token in annotated_tokens if self.valid_token(token)]

    def valid_token(self, token):
        return (
            token.is_alpha and                    # token is alpha numeric
            token.pos_ in ["PROPN", "NOUN"] and   # token is either noun or proper noun
            not token.is_punct and                # token is not punctuation
            not token.is_stop and                 # token is not is not a stop word
            token not in self.en_most_common and  # token is not one of english's most used words
            len(token) > 2
        )

    @staticmethod
    def load_en_most_common_file(file_path: str = EN_MOST_COMMON_FILE):
        with open(file_path, "r") as f:
            return [word for word in f.read().split("\n")]

    def cleanup_en_most_common_words(self, text_list: List[str]) -> List[str]:
        return [word for word in text_list if word not in self.en_most_common]

    @staticmethod
    def query_wikipedia(text):
        return {text: [w.lower() for w in wikipedia.search(text)]}

    async def summarize(self, rss_data: RSSData):
        # We will apply and combine several heuristics to achieve significant keyword extraction

        # Phase #1 - First step we need to cleanup and tokenize our data
        # Basic cleanup alone, could possibly at times result at nice keyword extraction
        tokens = self.cleanup(self.annotate(rss_data.title + ". " + rss_data.content))

        # Phase #2 - Outlier detection using IQR
        word_count = Counter(tokens)
        values = list(word_count.values())
        quartile_1, quartile_3 = np.percentile(values, [25, 75])
        iqr = quartile_3 - quartile_1
        upper_bound = quartile_3 + (iqr * 1.5)
        filtered_words = [k for k, v in word_count.items() if v > upper_bound]

        # Phase #3 - Validation thorough Wikipedia
        futures = [self.loop.run_in_executor(self.executor, self.query_wikipedia, word) for word in filtered_words]
        await asyncio.wait(futures)

        wiki_results = dict(ChainMap(*[f.result() for f in futures]))
        wikipedia_validated = [word for word in filtered_words if word in wiki_results.get(word, False)]

        return wikipedia_validated
