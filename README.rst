Davis weatherlink scraper/parser
================================

.. image:: https://travis-ci.org/ojarva/davis-weatherlink-scraper.svg?branch=master
    :target: https://travis-ci.org/ojarva/davis-weatherlink-scraper

Installation:

::

  pip install davis_weatherlink_scraper

or clone `the repository <https://github.com/ojarva/davis_weatherlink_scraper>`_ and run

::

  python setup.py install

Usage:

::

  import davis_weatherlink_scraper
  scraper = davis_weatherlink_scraper.WeatherLink()
  print scraper.get("hsksatama")
