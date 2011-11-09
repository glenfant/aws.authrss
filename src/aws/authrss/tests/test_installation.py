# -*- coding: utf-8 -*-
# $Id$
"""Testing the installation"""
import unittest2 as unittest
from aws.authrss.tests.resources import AWS_AUTHRSS_INTEGRATION_TESTING

from zope.interface.verify import verifyObject
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils as browserlayer_utils

from aws.authrss.interfaces import IAuthRSSLayer, ITokenManager


class TestInstallation(unittest.TestCase):

    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        return

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product installed
        """
        pid = 'aws.authrss'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        "Package appears not to have been installed")
        return

    def test_layer_available(self):
        """The layer is installed
        """
        self.assertTrue(IAuthRSSLayer in browserlayer_utils.registered_layers(),
                       "Our browser layer is not installed")
        return

    def test_componentregistry(self):
        """Our local utility (tokensmanager) is available
        """
        tokens_mgr = getUtility(ITokenManager)
        self.assertTrue(ITokenManager.providedBy(tokens_mgr))
        self.assertTrue(verifyObject(ITokenManager, tokens_mgr))
        return
