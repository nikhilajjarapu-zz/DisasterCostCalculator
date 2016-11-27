#!/usr/bin/env python

# Landsat Util
# License: CC0 1.0 Universal

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from landsat import __version__


def readme():
    with open('README.rst') as f:
        return f.read()

test_requirements = [
  'nose>=1.3.7',
  'mock>=1.3.0'
]

setup(
    name='landsat-util',
    version=__version__,
    description='A utility to search, download and process Landsat 8' +
    ' satellite imagery',
    long_description=readme(),
    author='Development Seed',
    author_email='info@developmentseed.org',
    scripts=['bin/landsat'],
    url='https://github.com/developmentseed/landsat-util',
    packages=['landsat'],
    include_package_data=True,
    license='CCO',
    platforms='Posix; MacOS X; Windows',
    install_requires=[
      'requests==2.7.0',
      'python-dateutil>=2.4.2',
      'numpy>=1.9.3',
      'termcolor>=1.1.0',
      'rasterio>=0.26.0',
      'six==1.9.0',
      'scipy>=0.16.0',
      'scikit-image>=0.11.3',
      'homura>=0.1.2',
      'boto>=2.38.0',
      'polyline==1.1'
    ],
    test_suite='nose.collector',
    tests_require=test_requirements
)
