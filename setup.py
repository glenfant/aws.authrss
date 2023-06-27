"""aws.authrss packaging utility"""

from setuptools import find_packages
from setuptools import setup

import os


def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path).read().strip()


version = "3.0.0.dev0"

long_description = "\n\n".join(
    [
        open("README.md").read(),
        open("CONTRIBUTORS.md").read(),
        open("CHANGES.md").read(),
    ]
)

setup(
    name="aws.authrss",
    version=version,
    description="Private Plone RSS feeds through a user private token",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: German",
    ],
    keywords="plone rss",
    author="Gilles Lenfant",
    author_email="gilles.lenfant@alterway.fr",
    url="http://pypi.python.org/pypi/aws.authrss",
    project_urls={
        "PyPI": "https://pypi.org/project/aws.authrss/",
        "Source": "https://github.com/collective/aws.authrss",
        "Tracker": "https://github.com/collective/aws.authrss/issues",
    },
    license="GPL",
    python_requires=">3.7",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["aws"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.GenericSetup",
        "Plone",
    ],
    extras_require={
        "test": [
            "lxml",
            "Plone",
            "Products.CMFCore",
            "plone.app.testing",
            "plone.testing>=5.0.0",
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = aws.authrss.locales.update:update_locale
    """,
)
