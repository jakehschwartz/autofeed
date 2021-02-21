# autofeed
Automated RSS Feed Reader

This is an RSS feed reader that will find new entries since the last time
checked and send them to your email. It also supports filtering articles
by keywords.

## Features

- Reads RSS streams to look for new articles since last read
- Sends articles via EMail (only works for GMail at the moment)
- Allows for filtering of articles by looking for keywords in the title and/or description

## Setup

1. Download file
2. Create .autofeed direction in $HOME
3. Create X.json file in .autofeed with the following syntax:
```
```
4. Run python autofeed.py list to verify
5. ???

## Development

Uses pipenv to manage the environment; run `pipenv shell` after cloning.
