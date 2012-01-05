# -*- coding: utf-8 -*-
# $Id$
"""Token manager tests"""
import unittest2 as unittest
from aws.authrss.tests.resources import AWS_AUTHRSS_INTEGRATION_TESTING

from zope.interface.verify import verifyObject
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from aws.authrss.interfaces import ITokenManager


class TestTokenManager(unittest.TestCase):

    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.token_mgr = getUtility(ITokenManager)
        self.bar_token = self.token_mgr.tokenForUserId('bar')
        return

    def test_interface(self):
        """The ITokenManager interface is fully implemented
        """
        self.assertTrue(verifyObject(ITokenManager, self.token_mgr),
                        "Interface is not fully implemented")
        return

    def test_new_token(self):
        """Getting the token for a new user
        """
        value = self.token_mgr.resetToken('foo')
        self.assertEqual(self.token_mgr.tokenForUserId('foo'), value,
                         "We should have the same token")
        return

    def test_user_for_token(self):
        """Providing a token
        """
        self.assertEqual(self.bar_token, self.token_mgr.tokenForUserId('bar'),
                         "Expected bar as owner of token")
        return

    def test_token_for_user(self):
        """Providing an user id
        """
        self.assertEqual('bar', self.token_mgr.userIdForToken(self.bar_token),
                         "Expected bar as owner of token")
        return

    def test_prune(self):
        """Pruning a (supposed) removed user
        (keep this test in last position)
        """
        self.token_mgr.pruneUserId('bar')
        self.assertEqual(len(self.token_mgr._token2uid), 0,
                         "There should be 0 stored token/user id")
        return
