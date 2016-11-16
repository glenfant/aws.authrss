# -*- coding: utf-8 -*-
"""Viewlets"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.links.viewlets import RSSViewlet
from aws.authrss.utils import AuthRSSViewMixin


class AuthRSSLinkViewlet(RSSViewlet, AuthRSSViewMixin):
    """We override the standard RSS link viewlet
    """
    def update(self):
        super(AuthRSSLinkViewlet, self).update()
        if not self.isUserAnonymous():
            for rsslink in self.rsslinks:
                if rsslink['url'].endswith('RSS'):
                    rsslink['url'] = self.authRSSFolderishLink()

    index = ViewPageTemplateFile('templates/rsslink.pt')

