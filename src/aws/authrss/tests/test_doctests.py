# -*- coding: utf-8 -*-
"""Running doctests"""

import unittest
import doctest

from plone.testing import layered

from aws.authrss.tests.resources import AWS_AUTHRSS_FUNCTIONAL_TESTING

def test_suite():
    test_files = ['use_cases.txt']
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(
                    *test_files,
                    optionflags=doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE),
                layer = AWS_AUTHRSS_FUNCTIONAL_TESTING),
    ])
    return suite
