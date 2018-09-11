from setuptools import setup, find_packages

setup(
    name='feed_summarizer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'wikipedia',
        'spacy',
        'numpy',
        'pyDAL',
        'feedparser',
        'nltk',
    ],
    entry_points='''
        [console_scripts]
        feed_summarizer=feedburner_summarizer.feedburner_summarizer.feed_summarizer:cli
    ''',
)
