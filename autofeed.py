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
parser.add_argument('--list', action='store_true', help='list all feed')
parser.add_argument('--gmail-username', help='username for gmail user')
parser.add_argument('--gmail-password', help='password for gmail user')
args = parser.parse_args()

# Get a list of feeds
feeds = os.listdir('./feeds/')
feed_map = {f[0:-5]: json.load(open(f'./feeds/{f}',)) for f in feeds}

if args.list:
    output = ""
    for key, entries in feed_map.items():
      output += f"{key}\n"
      for e in entries:
        output += f"{e}\n"
      output += "\n"
    print(output)
else:
    # Read the feeds
    msgs = {}
    for feed_type, feeds in feed_map.items():
      now = datetime.datetime.utcnow()
      new_feeds = []
      article_map = {}
      for feed in feeds:
        d = feedparser.parse(feed['url'])
        time = feed.get('last_read',now - datetime.timedelta(days = 30))
        entries = [e for e in d.entries if datetime.datetime.fromtimestamp(mktime(e.published_parsed)) > time]
        if len(entries):
          article_map[d.feed.title] = entries
        new_feeds.append({'url':feed['url'], 'time':now.isoformat()})

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

      # After checking everything, save time per list
      with open(f"./feeds/{feed_type}.json", "w") as outfile:
        json.dump(new_feeds, outfile)

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

