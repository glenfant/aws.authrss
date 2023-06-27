"""Testing resources from utils module"""

from AccessControl import getSecurityManager
from aws.authrss.interfaces import ITokenManager
from aws.authrss.testing import AWS_AUTHRSS_INTEGRATION_TESTING
from aws.authrss.utils import GrantPrivilegesForToken
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility

import unittest


class TestUtils(unittest.TestCase):
    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.token_mgr = getUtility(ITokenManager)
        self.bar_token = self.token_mgr.tokenForUserId(TEST_USER_ID)
        return

    def test_grant_privileges(self):
        """Testing GrantPrivilegesForToken context manager"""
        portal = self.portal
        logout()
        roles = getSecurityManager().getUser().getRolesInContext(portal)
        self.assertEqual(roles, ["Anonymous"])

        # We grant temporarily privileges of a real user to anonymous
        with GrantPrivilegesForToken(self.bar_token, portal):
            expected = {"Member", "Authenticated"}
            roles = getSecurityManager().getUser().getRolesInContext(portal)
            self.assertEqual(set(roles), expected)

        # We should have the former privileges since we left the context manager
        roles = getSecurityManager().getUser().getRolesInContext(portal)
        self.assertEqual(roles, ["Anonymous"])

        # But there should be no change in security with a junk token
        with GrantPrivilegesForToken("unknown-token", portal):
            roles = getSecurityManager().getUser().getRolesInContext(portal)
            self.assertEqual(roles, ["Anonymous"])
        return
