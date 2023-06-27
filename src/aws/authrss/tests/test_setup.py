"""Setup tests for this package."""
from aws.authrss.testing import AWS_AUTHRSS_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that aws.authrss is properly installed."""

    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if aws.authrss is installed."""
        self.assertTrue(self.installer.is_product_installed("aws.authrss"))

    def test_browserlayer(self):
        """Test that IAuthRSSLayer is registered."""
        from aws.authrss.interfaces import IAuthRSSLayer
        from plone.browserlayer import utils

        self.assertIn(IAuthRSSLayer, utils.registered_layers())

    def test_componentregistry(self):
        from aws.authrss.interfaces import ITokenManager
        from zope.component import queryUtility
        from zope.interface.verify import verifyObject

        """Our local utility (tokensmanager) is available"""
        tokens_mgr = queryUtility(ITokenManager)
        self.assertTrue(ITokenManager.providedBy(tokens_mgr))
        self.assertTrue(verifyObject(ITokenManager, tokens_mgr))


class TestUninstall(unittest.TestCase):
    layer = AWS_AUTHRSS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("aws.authrss")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if aws.authrss is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("aws.authrss"))

    def test_browserlayer_removed(self):
        """Test that IAuthRSSLayer is removed."""
        from aws.authrss.interfaces import IAuthRSSLayer
        from plone.browserlayer import utils

        self.assertNotIn(IAuthRSSLayer, utils.registered_layers())
