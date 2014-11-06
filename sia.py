#!/usr/bin/env python2

import os, os.path
from os.path import join
import datetime as dt
import time, pytz
import urllib
import calendar
import icalendar
import argparse
import re
from operator import itemgetter


# settings
ical_age_limit = 3600 * 12;


# functions

def events_date(cal, event_date, location=False, description=False):
  print event_date.strftime("%A, %x:")

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

    summary = component.get('summary')

    loc_str = ''
    if location:
      loc = component.get('location')
      loc_str = '\n                 %s' % loc

    desc_str = ''
    if location:
      desc = component.get('description')
      desc_str = '\n                 %s' % desc

    p = '  %s - %s: %s%s%s' % (start.strftime('%H:%M'), end.strftime('%H:%M'),\
                               summary, desc_str, loc_str)
    print p.encode('utf-8')


  return ''


# setup and parse arguments

app_path = os.path.dirname(os.path.realpath(__file__))
url_file = join(app_path, 'urls')
cache_file = join(app_path, 'cache.ics')
filter_file = join(app_path, 'filters')
tz_file = join(app_path, 'timezone')

parser = argparse.ArgumentParser(description='A remote ical aggregator.')
parser.add_argument('-s', dest='day', action='store_true', default=False, help='Display single day (default).')
parser.add_argument('-w', dest='week', action='store_true', default=False, help='Display week.')
parser.add_argument('-m', dest='month', action='store_true', default=False, help='Display month.')
parser.add_argument('-q', dest='quiet', action='store_true', default=False, help='Don\'t show any output. Useful in combination with -r.')
parser.add_argument('-o', dest='offset', metavar='n', type=int, action='store', default=0, help='Numerical offset from today, this week, or this month.')
parser.add_argument('-d', dest='description', action='store_true', default=False, help='Display event description.')
parser.add_argument('-l', dest='location', action='store_true', default=False, help='Display event location.')
parser.add_argument('-r', dest='force_retrieve', action='store_true', default=False, help='Force retrieving remote icals.')
parser.add_argument('-n', dest='no_retrieve', action='store_true', default=False, help='Don\'t allow retrieving remote icals, abort if no cache file is present. This overrides -r.')

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


# set time zone

with open(tz_file) as f:
  tz = f.read().rstrip()

tzlocal = pytz.timezone(tz)


# load urls

with open(join(app_path, "urls")) as f:
  urls = f.readlines()


# retrieve icals if neccessary

read = False
cal_string = ""

if not args.no_retrieve:

  if (args.force_retrieve
    or not os.path.exists(cache_file)
    or time.time() - os.path.getmtime(cache_file) > ical_age_limit):
    print "Retrieving icals...",
    
    f = open(cache_file, "wb")

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
    read = True

elif not os.path.exists(cache_file):
  print "Cache file doesn't exist, aborting."
  exit(1)

else:
  read = True

if read:
  f = open(cache_file, "r")
  cal_string = f.read()
  f.close()


# quiet option

if args.quiet:
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

target = dt.date.today()

if args.month:

  if args.offset != 0:
    target = target + dt.timedelta(days=args.offset*365/12)

  first_offset = -1 * (target.day - 1)
  target = target + dt.timedelta(days=first_offset)
  cur = target

  last = calendar.monthrange(target.year, target.month)[1]
  for day in range(0, last):
    cur = target + dt.timedelta(days=day)
    print events_date(cals, cur, location=args.location)

elif args.week:

  if args.offset != 0:
    target = target + dt.timedelta(weeks=args.offset)

  monday_offset = -1 * target.weekday()
  target = target + dt.timedelta(days=monday_offset)
  cur = target

  for day in range(0, 7):
    cur = target + dt.timedelta(days=day)
    print events_date(cals, cur, location=args.location)

else:
  if args.offset != 0:
    target = dt.date.today() + dt.timedelta(days=args.offset)

  print events_date(cals, target, location=args.location)
