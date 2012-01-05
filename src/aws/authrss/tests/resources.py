# -*- coding: utf-8 -*-
# $Id$
"""Test fixures and resources"""

from cStringIO import StringIO
from lxml import etree

from plone.app.testing import (
    PLONE_FIXTURE, PloneSandboxLayer, IntegrationTesting, FunctionalTesting,
    applyProfile, login, logout, setRoles,
    SITE_OWNER_NAME, SITE_OWNER_PASSWORD,
    TEST_USER_NAME, TEST_USER_ID, TEST_USER_PASSWORD
    )

from zope.configuration import xmlconfig


class AwsAuthrss(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import aws.authrss
        xmlconfig.file('configure.zcml',
                       aws.authrss,
                       context=configurationContext)
        return

    def setUpPloneSite(self, portal):
        # Why the f...k do we need to run the standard workflow GS step?
        setuptool = portal['portal_setup']
        setuptool.runImportStepFromProfile('profile-Products.CMFPlone:plone', 'workflow',
                                           run_dependencies=False)

        # Applying our default GS setup
        applyProfile(portal, 'aws.authrss:default')

        # Enabling global site syndication
        syntool = portal['portal_syndication']
        syntool.editProperties(isAllowed=True)
        return

AWS_AUTHRSS_FIXTURE = AwsAuthrss()

AWS_AUTHRSS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AWS_AUTHRSS_FIXTURE,),
    name="AwsAuthrss:Integration")


class AuthRssFunctionalTesting(FunctionalTesting):
    """Our layer for doctests
    """

    def anonymous_browser(self):
        """Browser of anonymous
        """
        from plone.testing.z2 import Browser
        browser = Browser(self['app'])
        browser.handleErrors = False
        return browser

    def _auth_browser(self, login, password):
        """Browser of authenticated user
        """
        import base64
        browser = self.anonymous_browser()

        basic_auth = 'Basic {0}'.format(
            base64.encodestring('{0}:{1}'.format(login, password))
            )
        browser.addHeader('Authorization', basic_auth)
        return browser

    def manager_browser(self):
        """Browser with Manager authentication
        """
        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def member_browser(self):
        """Browser with Member authentication
        """
        return self._auth_browser(TEST_USER_NAME, TEST_USER_PASSWORD)

    def enable_syndication(self, item):
        """Grants syndication shortcut
        """
        # FIXME: login(portal, SITE_OWNER_NAME) raises an AttributeError
        # That's why the TEST_USER_NAME has temporarily the Manager role
        # TODO: file an issue if there is a tracker
        from AccessControl import getSecurityManager
        portal = self['portal']
        login(portal, TEST_USER_NAME)
        tu_roles = getSecurityManager().getUser().getRolesInContext(portal)
        setRoles(portal, TEST_USER_ID, tu_roles+['Manager'])
        syntool = portal['portal_syndication']
        syntool.enableSyndication(item)
        setRoles(portal, TEST_USER_ID, tu_roles)
        logout()
        return

    def rss_feed_urls(self, feed):
        """URLs of an RSS feed
        :param feed: an RSS feed as XML string
        """
        namespaces = {
            'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            'dc': "http://purl.org/dc/elements/1.1/",
            'syn': "http://purl.org/rss/1.0/modules/syndication/",
            'rss': "http://purl.org/rss/1.0/"
            }
        feed_file = StringIO(feed)
        feed_tree = etree.parse(feed_file)
        return feed_tree.xpath('//rss:items//rdf:li/@rdf:resource',
                               namespaces=namespaces)


AWS_AUTHRSS_FUNCTIONAL_TESTING = AuthRssFunctionalTesting(
    bases=(AWS_AUTHRSS_FIXTURE,),
    name="AwsAuthrss:Functional")
