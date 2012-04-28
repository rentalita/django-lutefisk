# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

PACKAGE = os.environ['PACKAGE']
VERSION = os.environ['VERSION']

setup(name=PACKAGE, version=VERSION,
      packages=find_packages('src/python'), package_dir={'': 'src/python'},
      author='Rentalita',
      author_email='hello@rentalita.com',
      description='Django Lutefisk is a Django user account management app with an API.',
      url='http://rentalita.github.com/django-lutefisk',
      include_package_data=True,
)

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
