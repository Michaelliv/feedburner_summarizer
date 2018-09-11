# FeedBurner Summarizer
[Feedburner RSS](https://feedburner.google.com/) summarizer
* Free software: MIT license

## Features
* Reads and summarizers any feedburner RSS feed
* Has tests

Usage
-----
1) Fork repo
```
git@github.com:Michaelliv/feedburner_summarizer.git
```
2) Navigate to project directory

3) Install requirements

```
pip install -r requirments.txt
```

4) Download spacy english corpus

```
python -m spacy download en
```

5) Run script
```
python main.py --name [FEED_NAME] --iqr-enabled/--iqr-disabled --nouns-enabled/--nouns-disabled
```
