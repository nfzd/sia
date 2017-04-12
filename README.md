sia
===

sia is a simple ical aggregator in alpha stage.

Features:

- retrieve multiple remote icals
- filter events with regex-based filters
- display events of a day, week or month
- so far command line based, KISS

This is very much work in progress.


Usage
===

sia depends on [icalendar](https://pypi.python.org/pypi/icalendar). For installation, see their page.

sia is configured via text files in the ~/.sia/ directory. These files are:
- __urls__ : on remote ical location per line
- __filters__ : if an event summary matches on of the lines, it is not displayed

For more on usage, try --help.
