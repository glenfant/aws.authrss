# -*- coding: utf-8 -*-
"""Viewlets"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase

from aws.authrss.utils import AuthRSSViewMixin


class AuthRSSLinkViewlet(ViewletBase, AuthRSSViewMixin):
    def update(self):
        if self.isUserAnonymous():
            self.url = self.context.restrictedTraverse('@@syndication-util/rss_url')()
        else:
            self.url = self.authRSSFolderishLink()

    index = ViewPageTemplateFile('templates/rsslink.pt')
