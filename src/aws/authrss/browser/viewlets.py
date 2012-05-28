# -*- coding: utf-8 -*-
# $Id$
"""Viewlets"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.links.viewlets import RSSViewlet
from aws.authrss.utils import AuthRSSViewMixin


class AuthRSSLinkViewlet(RSSViewlet, AuthRSSViewMixin):
    """We override the standard RSS link viewlet
    """
    def update(self):
        """Note that update-ing parent class provides attributes:
        - 'allowed'
        - 'url': The RSS URL is 'allowed' is True
        """
        super(AuthRSSLinkViewlet, self).update()
        if self.allowed and not self.isUserAnonymous():

            # Okay we may rebuild the URL
            self.url = self.authRSSFolderishLink()
        return


    index = ViewPageTemplateFile('templates/rsslink.pt')

