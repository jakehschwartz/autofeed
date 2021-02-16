import datetime
import feedparser
import json
import os

from time import mktime

# Get a list of feeds
feeds = os.listdir('./feeds/')
feed_map = {f[0:-4]: open(f'./feeds/{f}',).readlines() for f in feeds}
filtered_feed_map = {k:list(filter(None, list(map(str.strip, v)))) for k, v in feed_map.items()}
print(filtered_feed_map)

# Get the last saved time per set of feeds
times = {key: datetime.datetime.fromisoformat(value) for key, value in json.load(open('times.json',)).items()}

# Config a place to send things

# Read the feeds
new_times = {}
for feed_type, feeds in filtered_feed_map.items():
  print("==============")
  print(feed_type)
  now = datetime.datetime.utcnow()
  time = times.get(feed_type, now - datetime.timedelta(days = 30))
  for feed in feeds:
    d = feedparser.parse(feed)
    print(d.feed.title,':')
    for e in d.entries:
      published_date = datetime.datetime.fromtimestamp(mktime(e.published_parsed))
      if published_date > time:
        print(f"{e.title}: {e.link} ({published_date.isoformat()})")
    print("")
  new_times[feed_type] = now.isoformat()


# After checking everything, save time per list
with open("times.json", "w") as outfile:
  json.dump(new_times, outfile)
