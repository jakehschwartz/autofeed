import feedparser
import json
import os

from datetime import datetime
from time import mktime

# Get a list of feeds
feeds = os.listdir('./feeds/')
feed_map = {f[0:-4]: open(f'./feeds/{f}',).readlines() for f in feeds}
print(feed_map)

# Get the last saved time per set of feeds
times = {key: datetime.fromisoformat(value) for key, value in json.load(open('times.json',)).items()}
print(times)

# Config a place to send things

new_times = {}
for feed_type, feeds in feed_map.items():
  now = datetime.utcnow().isoformat()
  for feed in feeds:
    d = feedparser.parse(feed)
    print(d.feed)
    for e in d.entries:
      published_date = datetime.fromtimestamp(mktime(e.published_parsed))
      if published_date > times[feed_type]:
        print(f"{e.title}: {e.link} ({published_date.isoformat()})")
  new_times[feed_type] = now


# After checking everything, save time per list
with open("times.json", "w") as outfile:
  json.dump(new_times, outfile)
