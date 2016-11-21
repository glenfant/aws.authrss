# -*- coding: utf-8 -*-
"""Test fixures and resources"""

import base64
from cStringIO import StringIO
from lxml import etree

from plone.testing.z2 import Browser

from plone.app.testing import (
    PLONE_FIXTURE, PloneSandboxLayer, IntegrationTesting, FunctionalTesting,
    applyProfile, login, logout, setRoles,
    SITE_OWNER_NAME, SITE_OWNER_PASSWORD,
    TEST_USER_NAME, TEST_USER_ID, TEST_USER_PASSWORD
    )
from Products.CMFCore.utils import getToolByName
from plone.testing import z2

class AwsAuthrss(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes)
        # Load ZCML for this package
        import aws.authrss
        self.loadZCML(package=aws.authrss)

    def setUpPloneSite(self, portal):
        # Why the f...k do we need to run the standard workflow GS step?
        setuptool = portal['portal_setup']
        setuptool.runImportStepFromProfile('profile-Products.CMFPlone:plone', 'workflow',
                                           run_dependencies=False)

        applyProfile(portal, 'plone.app.contenttypes:default')
        # Applying our default GS setup
        applyProfile(portal, 'aws.authrss:default')
        z2.login(portal.getParentNode().acl_users, SITE_OWNER_NAME)
        # Enabling global site syndication
        syntool = getToolByName(portal, 'portal_syndication')
        syntool.editProperties(isAllowed=True)
        z2.logout()
        login(portal, TEST_USER_NAME)

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
        browser = Browser(self['app'])
        browser.handleErrors = False
        return browser

    def _auth_browser(self, login, password):
        """Browser of authenticated user
        :param login: A known user login
        :param password: The password for this user
        """
        browser = self.anonymous_browser()

        basic_auth = 'Basic {0}'.format(
            base64.encodestring('{0}:{1}'.format(login, password))
            )
        browser.addHeader('Authorization', basic_auth)
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

    def enable_syndication(self, item):
        """Grants syndication shortcut
        :param item: Plone folder or topic
        """
        # FIXME: login(portal, SITE_OWNER_NAME) raises an AttributeError
        # That's why the TEST_USER_NAME has temporarily the Manager role
        # TODO: file an issue if there is a tracker
        from AccessControl import getSecurityManager
        portal = self['portal']
        login(portal, TEST_USER_NAME)
        tu_roles = getSecurityManager().getUser().getRolesInContext(portal)
        setRoles(portal, TEST_USER_ID, tu_roles+['Manager'])
        syntool = getToolByName(portal, 'portal_syndication')
        syntool.enableSyndication(item)
        setRoles(portal, TEST_USER_ID, tu_roles)
        logout()
        return

    def rss_feed_urls(self, feed):
        """URLs of an RSS feed
        :param feed: an RSS feed as XML string
        :return: sequence of tarrget URLs of the feed
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
