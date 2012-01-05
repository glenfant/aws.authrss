# -*- coding: utf-8 -*-
"""aws.authrss packaging utility"""

from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = read('src', 'aws', 'authrss', 'version.txt')

long_description = (
    read('README.rst')
    + '\n\n' +
    'Contributors\n'
    '============\n'
    + '\n\n' +
    read('CONTRIBUTORS.txt')
    + '\n\n' +
    read('CHANGES.txt')
    + '\n')

setup(name='aws.authrss',
      version=version,
      description="Private Plone RSS feeds through a user private token",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python :: 2.6",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Natural Language :: English",
          "Natural Language :: French",
          "Development Status :: 3 - Alpha",
          ],
      keywords='plone rss',
      author='Gilles Lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='http://pypi.python.org/pypi/aws.authrss',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['aws'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing', 'lxml']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
