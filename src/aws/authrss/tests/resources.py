# -*- coding: utf-8 -*-
# $Id$
"""Test fixures and resources"""

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig


class AwsAuthrss(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import aws.authrss
        xmlconfig.file('configure.zcml',
                       aws.authrss,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'aws.authrss:default')

AWS_AUTHRSS_FIXTURE = AwsAuthrss()
AWS_AUTHRSS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AWS_AUTHRSS_FIXTURE,),
    name="AwsAuthrss:Integration")
