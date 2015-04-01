#!/usr/bin/env python2

from distutils.core import setup

setup(
    name='sia',
    version='0.1.0',
    description='Simple ical aggregator.',
    author='Michael Mueller',
    author_email='world@nfzd.net',
    url='http://www.github.com/nfzd/sia',
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    #packages=['sia'],
    scripts=['bin/sia'],
    install_requires=["icalendar", "pytz"],
)
