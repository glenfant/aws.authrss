# -*- coding: utf-8 -*-
# $Id$
"""Testing browser view classes"""

import unittest2 as unittest
from aws.authrss.tests.resources import AWS_AUTHRSS_INTEGRATION_TESTING
from plone.app.testing import (
    logout, login, setRoles, TEST_USER_NAME, TEST_USER_ID, TEST_USER_ROLES
    )
from zope.interface import alsoProvides
from zope.component import getUtility
from aws.authrss.interfaces import IAuthRSSLayer, ITokenManager

class TestViews(unittest.TestCase):
    """Resources in the browser subpackage
    """
    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.wf_tool = self.portal['portal_workflow']
        # Making a syndicatable folder
        setRoles(self.portal, TEST_USER_ID, TEST_USER_ROLES + ['Contributor', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'folder_a', title="Folder A")
        self.wf_tool.doActionFor(self.portal['folder_a'], 'publish')

        # FIXME: Why do we need to add explicitely our layer here when it is supposed
        # to be in the registered layers for this site (by its GS profile) ?
        alsoProvides(self.portal['folder_a'].REQUEST, IAuthRSSLayer)
        return

    def test_anon_rss_link(self):
        """Anonymous have the usual RSS link
        """
        logout()
        folder_a = self.portal['folder_a']
        link_view = folder_a.restrictedTraverse('@@auth-rss-link')
        self.failUnless(link_view().endswith('/RSS'), "Should have the anonymous RSS URL")
        return

    def test_auth_rss_link(self):
        """Authenticated users have a personal RSS link
        """
        login(self.portal, TEST_USER_NAME)
        folder_a = self.portal['folder_a']
        token_mrg = getUtility(ITokenManager)
        token = token_mrg.tokenForUserId(TEST_USER_ID)
        expected = '/AUTH-RSS?token={0}'.format(token)
        link_view = folder_a.restrictedTraverse('@@auth-rss-link')
        self.failUnless(link_view().endswith(expected), "Should have an authenticated RSS URL")
        return

    def test_feed(self):
        """We add in folder_a a private content created by TEST_USER
        PRIVATE_USER should have it in his heed when the anonymous user should not
        """
        # FIXME: Do the test code
        return



