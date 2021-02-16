import argparse
import datetime
import feedparser
import json
import os
import smtplib, ssl
import sys

from time import mktime
from email.mime.text import MIMEText

parser = argparse.ArgumentParser(description='Auto RSS Reader')
parser.add_argument('--gmail-username', help='username for gmail user')
parser.add_argument('--gmail-password', help='password for gmail user')
args = parser.parse_args()

# Get a list of feeds
feeds = os.listdir('./feeds/')
feed_map = {f[0:-4]: open(f'./feeds/{f}',).readlines() for f in feeds}
filtered_feed_map = {k:list(filter(None, list(map(str.strip, v)))) for k, v in feed_map.items()}

# Get the last saved time per set of feeds
times = {key: datetime.datetime.fromisoformat(value) for key, value in json.load(open('times.json',)).items()}

# Read the feeds
new_times = {}
msgs = {}
for feed_type, feeds in filtered_feed_map.items():
  print("==============")
  now = datetime.datetime.utcnow()
  time = times.get(feed_type, now - datetime.timedelta(days = 30))
  article_map = {}
  for feed in feeds:
    d = feedparser.parse(feed)
    entries = [e for e in d.entries if datetime.datetime.fromtimestamp(mktime(e.published_parsed)) > time]
    if len(entries):
      article_map[d.feed.title] = entries
  
  if len(article_map):
    email_body = ""
    for key, entries in article_map.items():
      email_body += f"{key}\n"
      for e in entries:
        email_body += f"{e.title}: {e.link} ({datetime.datetime.fromtimestamp(mktime(e.published_parsed))})\n"
      email_body += "\n"

    subject = f'{len([x for _, i in article_map.items() if i for x in i])} new {feed_type} articles'
    message = f"{email_body}Love,\nAutofeed"

    msgs[feed_type] = (subject, message) 

  new_times[feed_type] = now.isoformat()

if args.gmail_username and args.gmail_password:
  sender = f'{args.gmail_username}@gmail.com'
  print("Sending emails to", sender,args.gmail_password)
  s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
  s.login(user = args.gmail_username, password = args.gmail_password)
  s.ehlo()
  for k, (subject, message) in msgs.items():
    print(subject)
    print(message)
    msg = MIMEText(message, _charset="UTF-8")
    msg['From'] = sender
    msg['To'] = sender
    msg['Subject'] = subject
    s.sendmail(sender, sender, msg.as_string())
  s.quit()

# After checking everything, save time per list
with open("times.json", "w") as outfile:
  json.dump(new_times, outfile)
