from typing import List

import itertools

import re
from nltk import sent_tokenize
from nltk.tokenize import ToktokTokenizer
from nltk.corpus import stopwords
from string import punctuation

from feedburner_summarizer.definitions import EN_MOST_COMMON_FILE
from feedburner_summarizer.rss_handler import RSSData

class DocSummarizer():

    def __init__(self):
        self.tokenizer = ToktokTokenizer()
        self.stopwords = set(stopwords.words('english'))
        self.en_most_common = set(self.load_en_most_common_file())
        self.escape_punct = re.compile("[{}]".format(re.escape(punctuation)))

    def load_en_most_common_file(self, file_path: str = EN_MOST_COMMON_FILE):
        with open(file_path, "r") as f:
            return [word for word in f.read().split("\n")]

    def cleanup_stopwords(self, text_list: List[str]) -> List[str]:
        return [word for word in text_list if word not in self.stopwords]

    def cleanup_en_most_common_words(self, text_list: List[str]) -> List[str]:
        return [word for word in text_list if word not in self.en_most_common]

    def cleanup_punctuation(self, text: str) -> str:
        return self.escape_punct.sub('', text)

    def tokenize_words(self, words: str) -> List[str]:
        return self.tokenizer.tokenize(words)

    def tokenize_sentences(self, text: str) -> List[str]:
        return sent_tokenize(text)

    def standard_cleanup_pipe(self, text: str) -> List[str]:
        sentences = sent_tokenize(text.lower())
        words = list(itertools.chain(*[self.tokenize_words(self.cleanup_punctuation(sentence)) for sentence in sentences]))
        return self.cleanup_stopwords(self.cleanup_en_most_common_words(words))

    def summarize(self, rss_data: RSSData):
        title_tokens = self.standard_cleanup_pipe(rss_data.title)
        content_tokens = self.standard_cleanup_pipe(rss_data.content)
