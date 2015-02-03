#!/usr/bin/env python2

import argparse
import calendar
import datetime as dt
import icalendar
from operator import itemgetter
import os, os.path
from os.path import join
import pytz
import re
import sys
import time
import tzlocal
import urllib


# settings
ical_age_limit = 3600 * 12;


# functions

def exit(error_msg):
    sys.exit(os.path.basename(__file__) + ": Error: " + error_msg)

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
    if description:
      desc = component.get('description')
      desc_str = '\n                 %s' % desc

    p = '  %s - %s: %s%s%s' % (start.strftime('%H:%M'), end.strftime('%H:%M'),\
                               summary, desc_str, loc_str)
    print p.encode('utf-8')


  return ''


if __name__ == '__main__':

    # setup file names

    home = os.path.expanduser("~")
    confdir = join(home, '.sia')
    url_file = join(confdir, 'urls')
    filter_file = join(confdir, 'urls')
    cache_file = join(confdir, 'cache.ics')

    # parse arguments

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
      err =  "Error: conflicting flags (",
      if args.day:
        err += "-d",
      if args.week:
        err += "-w",
      if args.month:
        err += "-m",
      err += "). Aborting."

      exit(err)

    
    # get time zone

    tzlocal = tzlocal.get_localzone()


    # load config files

    if not os.path.exists(url_file):
      exit('url file not found (should be at ~/.sia/urls).')
    else:
      with open(url_file) as f:
        urls = f.readlines()

    if not os.path.exists(filter_file):
      filters = []
    else:
      with open(filter_file) as f:
        filters = f.readlines()

      for i, elem in enumerate(filters):
        filters[i] = elem.rstrip('\n')


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
      exit("Cache file doesn't exist, aborting.")

    else:
      read = True

    if read:
      with open(cache_file) as f:
        cal_string = f.read()


    # quiet option

    if args.quiet:
      sys.exit()


    # load cals

    cals = icalendar.Calendar.from_ical(cal_string, multiple=True)


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
        print events_date(cals, cur, location=args.location, description=args.description)

    else:
      if args.offset != 0:
        target = dt.date.today() + dt.timedelta(days=args.offset)

      print events_date(cals, target, location=args.location)
