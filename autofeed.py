import argparse
import datetime
import feedparser
import json
import os
import smtplib, ssl
import sys

from time import mktime
from email.mime.text import MIMEText
from pathlib import Path

parser = argparse.ArgumentParser(description='Auto RSS Reader')
parser.add_argument('--show', action='store_true', help='show all feeds')
parser.add_argument('--gmail-username', help='username for gmail user')
parser.add_argument('--gmail-password', help='password for gmail user')
args = parser.parse_args()

# Get a list of feeds
file_location = f'{Path.home()}/.autofeed/feeds.json'
feed_map = json.load(open(file_location))

if args.show:
    output = ""
    for key, obj in feed_map.items():
      output += f"{key}\n"
      for f in obj['feeds']:
        output += f"{f}\n"
      output += "\n"
    print(output)
else:
    # Read the feeds
    msgs = {}
    new_feed_map = {}
    for feed_type, feeds_dict in feed_map.items():
      now = datetime.datetime.utcnow()
      new_feeds = []
      article_map = {}
      for feed in feeds_dict['feeds']:
        d = feedparser.parse(feed['url'])
        time = feed.get('last_read', (now - datetime.timedelta(days = 30)).isoformat())
        entries = [e for e in d.entries if datetime.datetime.fromtimestamp(mktime(e.published_parsed)) > datetime.datetime.fromisoformat(time)]
        if len(entries):
          article_map[d.feed.title] = entries
        new_feeds.append({'url':feed['url'], 'last_read':now.isoformat()})

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
        
      new_feed_map[feed_type] = {'feeds':new_feeds}  

   # After checking everything, save feeds with new times
    with open(file_location, "w") as outfile:
      json.dump(new_feed_map, outfile)

    if len(msgs):
      if args.gmail_username and args.gmail_password:
        sender = f'{args.gmail_username}@gmail.com'
        print("Sending emails to", sender,args.gmail_password)
        s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
        s.login(user = args.gmail_username, password = args.gmail_password)
        s.ehlo()
        for k, (subject, message) in msgs.items():
          print("==============")
          print(subject)
          print(message)
          msg = MIMEText(message, _charset="UTF-8")
          msg['From'] = sender
          msg['To'] = sender
          msg['Subject'] = subject
          s.sendmail(sender, sender, msg.as_string())
        s.quit()
      else:
        for k, (subject, message) in msgs.items():
          print("==============")
          print(subject)
          print(message)
    else:
        print("No new articles")

