#!/usr/bin/env python3

from setuptools import setup, find_packages
import sys

setup(
    zip_safe=True,
    name='unsubmail',
    version='1.0.0',
    long_description="Application for processing unsubscribe links in IMAP mail",
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Programming Language :: Python :: 3",
    ],
    keywords='imap spam',
    author='John Casey',
    author_email='jdcasey@commonjava.org',
    url='https://github.com/jdcasey/unsubmail',
    license='GPLv3+',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[
      "ruamel.yaml",
      "click",
      "requests",
      "beautifulsoup4"
    ],
    include_package_data=True,
    test_suite="tests",
    entry_points={
      'console_scripts': [
        'unsubmail = unsubmail:unsubscribe'
      ],
    }
)

