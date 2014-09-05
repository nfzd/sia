sia
===

sia is a simple ical aggregator in alpha stage.

Features:

- retrieving multiple remote icals
- filtering events with regex-based filters
- display events of a day, week (todo) or month (todo)
- so far a command line tool, KISS

This is very much work in progress.


Usage
===

sia depends on [https://pypi.python.org/pypi/icalendar](icalendar). For installation, see their page.

Currently, sia is configured via text files in the program directory. A file name __urls__ can contain one url per line, from where the remote icals are retrieved. A file named __filters__ contains custom filters. If sia finds a match of one on the filters on an event summary, the event is discarded.

For more on usage, try --help.
