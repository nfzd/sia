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

def display(cal):
  return cal.to_ical().replace('\r\n', '\n').strip()

def events_today(cal):
  return events_date(cal, dt.date.today())

def events_date(cal, event_date):
  print event_date.strftime("%Y-%m-%d:")

  events = []

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

  for event in events:
    start = event[0]
    component = event[1]
    dt_local = component.get('dtend').dt.astimezone(tzlocal) # localize time
    end = dt_local.time()
    print "  ", start.strftime("%H:%M"), "-", end.strftime("%H:%M"), component.get('summary')


  return ""


# setup and parse arguments

parser = argparse.ArgumentParser(description='A remote ical aggregator.')
# TODO implement week, month
parser.add_argument('-t', dest='target', choices=['day'], default='day', help='display time frame')
parser.add_argument('-o', dest='offset', metavar='n', type=int, action='store', default=0, help='numerical offset from today, this week, or this month')
args = parser.parse_args()


# retrieve icals if neccessary

app_path = os.path.dirname(os.path.realpath(__file__))
file_name = app_path + "/cache.ics"

if (not os.path.exists(file_name)
  or time.time() - os.path.getmtime(file_name) > ical_age_limit):
  print "Retrieving icals...",
  
  f = open(file_name, "wb")

  for url in urls:
    # TODO catch errors
    u = urllib.urlopen(url, file_name)
    buf = u.read()
    f.write(buf)

  f.close()

  print "done."

else:

  f = open(file_name, "r")
  buf = f.read()
  f.close()


# load cals

cal = icalendar.Calendar.from_ical(buf)


# import filter rules
with open(join(app_path, "filters")) as f:
  filters = f.readlines()

for i, elem in enumerate(filters):
  filters[i] = elem.rstrip('\n')


# display

if args.target == 'day':
  if args.offset == 0:
    print events_today(cal)
  else:
    target = dt.date.today() + dt.timedelta(days=args.offset)
    print events_date(cal, target)

