import asyncio
from collections import ChainMap
from collections import Counter
from typing import List, Dict

import numpy as np
import spacy
import wikipedia

from src.definitions import EN_MOST_COMMON_FILE
from src.rss_handler import RSSData


class DocSummarizer:
    def __init__(self, only_nouns_enabled = False, iqr_enabled = False):
        self.en_most_common = set(self.load_en_most_common_file())
        self.nlp = spacy.load('en')
        self.only_nouns_enabled = only_nouns_enabled
        self.iqr_enabled = iqr_enabled

    @staticmethod
    def load_en_most_common_file(file_path: str = EN_MOST_COMMON_FILE):
        with open(file_path, "r") as f:
            return [word for word in f.read().split("\n")]

    def annotate(self, text):
        return self.nlp(text)

    def process(self, annotated_tokens: List):
        return list(filter(self.cleanup, annotated_tokens))

    def cleanup(self, token):
        conditions =  (
            len(token) >= 2 and                    # token is shorter or equal to 2 characters
            token.is_alpha and                     # token is not alpha numeric
            not token.is_punct and                 # token is not punctuation
            not token.is_stop and                  # token is not is not a stop word
            token not in self.en_most_common       # token is not one of english's most used words
        )

        if self.only_nouns_enabled:
            conditions = conditions and (token.pos_ in ["PROPN", "NOUN"])  # token is either noun or proper noun

        return conditions

    @staticmethod
    def query_wikipedia(text: str) -> Dict:
        return {text: [w.lower() for w in wikipedia.search(text)]}

    @staticmethod
    def filter_by_iqr(tokens: List[str]):
        word_count = Counter(tokens)
        values = list(word_count.values())
        quartile_1, quartile_3 = np.percentile(values, [25, 75])
        iqr = quartile_3 - quartile_1
        upper_bound = quartile_3 + (iqr * 1.5)
        filtered_words = [k for k, v in word_count.items() if v > upper_bound]
        return filtered_words

    def math_filters(self, tokens):
        if self.iqr_enabled:
            tokens = self.filter_by_iqr(tokens)

        return tokens


    async def summarize(self, loop, executor, rss_data: RSSData):
        # We will process the text in multiple ways to achieve to have an easier job at extracting significant key words

        # First we pre-process the texts:
        # Lower case everything
        # Remove very short strings
        # Remove non alpha-numeric strings
        # Remove punctuation
        # Remove stopwords
        # Remove the most frequently used words in english
        # Tokenize and lemmatize the text

        # Cleanup:
        tokens = self.process(self.annotate((rss_data.title + " " + rss_data.content).lower()))
        lemmatized_tokens = [t.lemma_ for t in tokens]

        # Mathematical filters
        filtered = set(self.math_filters(lemmatized_tokens))

        # Remove extremely rare words (using wikipedia)
        futures = [loop.run_in_executor(executor, self.query_wikipedia, word) for word in filtered]

        if futures:
            await asyncio.wait(futures)

            wiki_results = dict(ChainMap(*[f.result() for f in futures]))
            wikipedia_validated = [word for word in filtered if word in wiki_results.get(word, False)]

            return wikipedia_validated
        else:
            return []
