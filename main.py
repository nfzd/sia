#!/usr/bin/env python2

import os, os.path
from os.path import join
import datetime as dt
import time, pytz
import urllib
import icalendar
import argparse
import re
from operator import itemgetter


# settings
ical_age_limit = 3600 * 5;


# time zone handling
tzlocal = pytz.timezone('Europe/Berlin')


# functions

def events_today(cals):
  return events_date(cals, dt.date.today())

def events_date(cal, event_date):
  print event_date.strftime("%Y-%m-%d:")

  events = []

  for cal in cals:
    for component in cal.walk("VEVENT"):
      dtstart = component.get('dtstart').dt

      if dtstart.date() == event_date:
        dt_local = dtstart.astimezone(tzlocal) # localize time
        start = dt_local.time()

        # filter
        skip = False
        summary = component.get('summary')
        for f in filters:
          if re.search(f, summary):
            skip = True
            break

        if not skip:
          events.append( (start, component) )

  events.sort(key=itemgetter(0))

  for event in events:
    start = event[0]
    component = event[1]
    dt_local = component.get('dtend').dt.astimezone(tzlocal) # localize time
    end = dt_local.time()
    print "  ", start.strftime("%H:%M"), "-", end.strftime("%H:%M"), component.get('summary')


  return ""


# setup and parse arguments

app_path = os.path.dirname(os.path.realpath(__file__))
url_file = join(app_path, "urls")
cache_file = join(app_path, "cache.ics")
filter_file = join(app_path, "filters")

parser = argparse.ArgumentParser(description='A remote ical aggregator.')
# TODO implement week, month
parser.add_argument('-t', dest='target', choices=['day'], default='day', help='display time frame')
parser.add_argument('-o', dest='offset', metavar='n', type=int, action='store', default=0, help='numerical offset from today, this week, or this month')
args = parser.parse_args()


# load urls

with open(join(app_path, "urls")) as f:
  urls = f.readlines()


# retrieve icals if neccessary

if (not os.path.exists(cache_file)
  or time.time() - os.path.getmtime(cache_file) > ical_age_limit):
  print "Retrieving icals...",
  
  f = open(cache_file, "wb")
  cal_string = ""

  for url in urls:
    # TODO catch errors
    url = url.rstrip()
    u = urllib.urlopen(url, url_file)
    buf = u.read()
    cal_string += buf
    f.write(buf)

  f.close()

  print "done."

else:

  f = open(cache_file, "r")
  cal_string = f.read()
  f.close()


# load cals

cals = icalendar.Calendar.from_ical(cal_string, multiple=True)


# import filter rules
with open(filter_file) as f:
  filters = f.readlines()

for i, elem in enumerate(filters):
  filters[i] = elem.rstrip('\n')


# display

if args.target == 'day':
  if args.offset == 0:
    print events_today(cals)
  else:
    target = dt.date.today() + dt.timedelta(days=args.offset)
    print events_date(cals, target)

