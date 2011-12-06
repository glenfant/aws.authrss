# -*- coding: utf-8 -*-
# $Id$
"""Running doctests"""

import os
import unittest2 as unittest
import doctest

from plone.testing import layered

from aws.authrss.tests.resources import AWS_AUTHRSS_FUNCTIONAL_TESTING

def test_suite():
    test_files = ['use_cases.txt']
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(
                    *test_files,
                    optionflags=doctest.ELLIPSIS),
                layer = AWS_AUTHRSS_FUNCTIONAL_TESTING),
    ])
    return suite
