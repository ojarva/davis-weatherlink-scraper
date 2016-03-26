Davis weatherlink scraper/parser
================================

Installation:

::

  pip install davis_weatherlink_scraper

or clone `the repository <https://github.com/ojarva/davis_weatherlink_scraper>`_ and run

::

  python setup.py install

Usage:

::

  import davis_weatherlink_scraper
  scraper = WeatherLink()
  print scraper.get("hsksatama")
