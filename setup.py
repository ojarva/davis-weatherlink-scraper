from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='davis-weatherlink-scraper',
    version='0.1.0',
    description='Scraper and parser for Davis Weatherlink data',
    long_description=long_description,
    url='https://github.com/ojarva/davis-weatherlink-scraper',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='davis weatherlink weather',
    packages=["davis_weatherlink_scraper"],
    install_requires=['beautifulsoup4==4.4.1', 'requests==2.9.1', 'docopt==0.6.2', 'redis==2.10.5'],
    scripts=["davis_weatherlink_scraper/weatherlink_redis_publisher", "davis_weatherlink_scraper/weatherlink"],
    test_suite="tests",

    extras_require={
        'dev': ['twine', 'wheel'],
    },
)
