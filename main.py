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
parser.add_argument('-d', dest='day', action='store_true', default=False, help='Display single day (default).')
parser.add_argument('-w', dest='week', action='store_true', default=False, help='Display week.')
parser.add_argument('-m', dest='month', action='store_true', default=False, help='Display month.')
parser.add_argument('-n', dest='nop', action='store_true', default=False, help='Don\'t show any output. Useful in combination with -r.')
parser.add_argument('-o', dest='offset', metavar='n', type=int, action='store', default=0, help='Numerical offset from today, this week, or this month.')
parser.add_argument('-r', dest='force_retrieve', action='store_true', default=False, help='Force retrieving remote icals.')
parser.add_argument('--no-retrieve', dest='no_retrieve', action='store_true', default=False, help='Don\'t allow retrieving remote icals, abort if no cache file is present. This overrides -r.')

args = parser.parse_args()

# check for argument conflicts
if sum([ args.day, args.week, args.month ]) > 1:
  print "Error: conflicting flags (",
  if args.day:
    print "-d",
  if args.week:
    print "-w",
  if args.month:
    print "-m",

  print "). Aborting."
  exit(1)


# load urls

with open(join(app_path, "urls")) as f:
  urls = f.readlines()


# retrieve icals if neccessary

if not args.no_retrieve:

  if (args.force_retrieve
    or not os.path.exists(cache_file)
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

elif not os.path.exists(cache_file):
  print "Cache file doesn't exist, aborting."
  exit(1)

else:

  f = open(cache_file, "r")
  cal_string = f.read()
  f.close()


# nop option

if args.nop:
  exit(0)


# load cals

cals = icalendar.Calendar.from_ical(cal_string, multiple=True)


# import filter rules

if os.path.exists(filter_file):
  with open(filter_file) as f:
    filters = f.readlines()

  for i, elem in enumerate(filters):
    filters[i] = elem.rstrip('\n')
else:
  filters = []


# display

if args.month:

  print "Not implemented yet. Sorry."
  exit(1336)

elif args.week:

  print "Not implemented yet. Sorry."
  exit(1336)

else:

  if args.offset == 0:
    print events_today(cals)
  else:
    target = dt.date.today() + dt.timedelta(days=args.offset)
    print events_date(cals, target)

exit(0)
