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

parser = argparse.ArgumentParser(description="Auto RSS Reader")
parser.add_argument("--show", action="store_true", help="show all feeds")
parser.add_argument("--gmail-username", help="username for gmail user")
parser.add_argument("--gmail-password", help="password for gmail user")
args = parser.parse_args()

# Get a list of feeds
file_location = f"{Path.home()}/.autofeed/feeds.json"
feed_map = json.load(open(file_location))


def check_article(e, check_time, words):
    article_time = datetime.datetime.fromtimestamp(mktime(e.published_parsed))
    if article_time <= check_time:
        return False
    if not len(words):
        return True
    for w in words:
        if e.title.lower().find(w) != -1 and e.description.lower().find(w) != -1:
            return True
    return False


if args.show:
    output = ""
    for key, obj in feed_map.items():
        output += f"{key}: {obj['words']}\n"
        for f in obj["feeds"]:
            output += f"{f}\n"
    print(output)
else:
    # Read the feeds
    msgs = {}
    new_feed_map = {}
    for feed_type, feeds_dict in feed_map.items():
        now = datetime.datetime.utcnow()
        new_feeds = []
        article_map = {}
        words = feeds_dict.get("words", [])
        for feed in feeds_dict["feeds"]:
            d = feedparser.parse(feed["url"])
            timestr = feed.get(
                "last_read", (now - datetime.timedelta(days=30)).isoformat()
            )
            time = datetime.datetime.fromisoformat(timestr)

            entries = [e for e in d.entries if check_article(e, time, words)]
            if len(entries):
                article_map[d.feed.title] = entries
            new_feeds.append({"url": feed["url"], "last_read": now.isoformat()})

        if len(article_map):
            email_body = ""
            for key, entries in article_map.items():
                email_body += f"{key}\n"
                for e in entries:
                    email_body += f"{e.title}: {e.link} ({datetime.datetime.fromtimestamp(mktime(e.published_parsed))})\n"

            subject = f"{len([x for _, i in article_map.items() if i for x in i])} new {feed_type} articles"
            message = f"{email_body}\nLove,\nAutofeed"

            msgs[feed_type] = (subject, message)

        new_feed_map[feed_type] = {"feeds": new_feeds, "words": words}

    # After checking everything, save feeds with new times
    with open(file_location, "w") as outfile:
        json.dump(new_feed_map, outfile)

    if len(msgs):
        if args.gmail_username and args.gmail_password:
            sender = f"{args.gmail_username}@gmail.com"
            print("Sending emails to", sender, args.gmail_password)
            s = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
            s.login(user=args.gmail_username, password=args.gmail_password)
            s.ehlo()
            for k, (subject, message) in msgs.items():
                print("==============")
                print(subject)
                print(message)
                msg = MIMEText(message, _charset="UTF-8")
                msg["From"] = sender
                msg["To"] = sender
                msg["Subject"] = subject
                s.sendmail(sender, sender, msg.as_string())
            s.quit()
        else:
            for k, (subject, message) in msgs.items():
                print("==============")
                print(subject)
                print(message)
    else:
        print("No new articles")
