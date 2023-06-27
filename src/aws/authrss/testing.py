"""Test fixures and resources"""

from io import StringIO
from lxml import etree
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from plone.testing.zope import WSGI_SERVER_FIXTURE

import base64


class AwsAuthrss(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import aws.authrss

        self.loadZCML(name="configure.zcml", package=aws.authrss)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "aws.authrss:default")

        # load Upgrade Steps
        portal_setup = portal.portal_setup
        profile_id = "ukd.carusnet:default"
        portal_setup.setLastVersionForProfile(profile_id, "1")
        portal_setup.upgradeProfile(profile_id)

        # Why is this call needed!?
        setuptool = portal["portal_setup"]
        setuptool.runImportStepFromProfile(
            "profile-Products.CMFPlone:plone", "workflow", run_dependencies=False
        )


AWS_AUTHRSS_FIXTURE = AwsAuthrss()

AWS_AUTHRSS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AWS_AUTHRSS_FIXTURE,), name="AwsAuthrss:Integration"
)


class AuthRssFunctionalTesting(FunctionalTesting):
    """Our layer for doctests"""

    def anonymous_browser(self):
        """Browser of anonymous"""
        browser = Browser(self["app"])
        browser.handleErrors = False
        return browser

    def _auth_browser(self, login, password):
        """Browser of authenticated user
        :param login: A known user login
        :param password: The password for this user
        """
        browser = self.anonymous_browser()

        basic_auth = "Basic {}".format(base64.b64encode(f"{login}:{password}".encode()))
        browser.addHeader("Authorization", basic_auth)
        return browser

    def manager_browser(self):
        """Browser with Manager authentication
        :return: Browser object with manager HTTP basic authentication header
        """
        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def member_browser(self):
        """Browser with Member authentication
        :return: Browser object with member HTTP basic authentication header
        """
        return self._auth_browser(TEST_USER_NAME, TEST_USER_PASSWORD)

    def rss_feed_urls(self, feed):
        """URLs of an RSS feed
        :param feed: an RSS feed as XML string
        :return: sequence of tarrget URLs of the feed
        """
        namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "syn": "http://purl.org/rss/1.0/modules/syndication/",
            "rss": "http://purl.org/rss/1.0/",
        }
        feed_file = StringIO(feed)
        feed_tree = etree.parse(feed_file)
        return feed_tree.xpath(
            "//rss:items//rdf:li/@rdf:resource", namespaces=namespaces
        )


AWS_AUTHRSS_FUNCTIONAL_TESTING = AuthRssFunctionalTesting(
    bases=(
        AWS_AUTHRSS_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="AwsAuthrss:Functional",
)
