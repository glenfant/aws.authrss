"""Testing browser view classes"""

from aws.authrss.interfaces import IAuthRSSLayer
from aws.authrss.interfaces import ITokenManager
from aws.authrss.testing import AWS_AUTHRSS_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ROLES
from zope.component import getUtility
from zope.interface import alsoProvides

import unittest


class TestViews(unittest.TestCase):
    """Resources in the browser subpackage"""

    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.wf_tool = self.portal["portal_workflow"]
        # Making a syndicatable folder
        setRoles(
            self.portal, TEST_USER_ID, TEST_USER_ROLES + ["Contributor", "Reviewer"]
        )
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Folder", "folder_a", title="Folder A")
        self.wf_tool.doActionFor(self.portal["folder_a"], "publish")

        # FIXME: Why do we need to add explicitly our layer here when it is supposed
        # to be in the registered layers for this site (by its GS profile) ?
        alsoProvides(self.portal["folder_a"].REQUEST, IAuthRSSLayer)

    def test_anon_rss_link(self):
        """Anonymous have the usual RSS link"""
        logout()
        folder_a = self.portal["folder_a"]
        link_view = folder_a.restrictedTraverse("@@auth-rss-link")
        self.assertTrue(
            link_view().endswith("/RSS"), "Should have the anonymous RSS URL"
        )
        return

    def test_auth_rss_link(self):
        """Authenticated users have a personal RSS link"""
        login(self.portal, TEST_USER_NAME)
        folder_a = self.portal["folder_a"]
        token_mrg = getUtility(ITokenManager)
        token = token_mrg.tokenForUserId(TEST_USER_ID)
        expected = f"/AUTH-RSS?token={token}"
        link_view = folder_a.restrictedTraverse("@@auth-rss-link")
        self.assertTrue(
            link_view().endswith(expected), "Should have an authenticated RSS URL"
        )
        return

    def test_feed(self):
        """We add in folder_a a private content created by TEST_USER
        PRIVATE_USER should have it in his heed when the anonymous user should not
        """
        # FIXME: Do the test code
        return
