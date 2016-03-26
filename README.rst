Davis weatherlink scraper/parser
================================

This small library fetches status information from Huawei B593 4G modem.

Installation:

::

  pip install davis_weatherlink_scraper

or clone `the repository <https://github.com/ojarva/davis_weatherlink_scraper>`_ and run

::

  python setup.py install

Usage:

::

  import davis_weatherlink_scraper
  scraper =  = WeatherLink()
  print scraper.get("hsksatama")
