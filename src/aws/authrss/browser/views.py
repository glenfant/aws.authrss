# -*- coding: utf-8 -*-
# $Id$
"""Views (z3) for aws.authrss"""

from zope.component import getMultiAdapter, getUtility
from Products.Five import BrowserView
from aws.authrss.interfaces import ITokenManager
from aws.authrss.utils import GrantPrivilegesForToken


class RSSLinkView(BrowserView):
    """Builds the link for authenticated RSS
    """
    def __call__(self, *args, **kwargs):
        """Runs the view
        """
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        method = "/RSS"  # Fallback to default usual RSS
        if not portal_state.anonymous():

            # We have an authenticated member
            user_id = portal_state.member().getId()
            token_mgr = getUtility(ITokenManager)
            token = token_mgr.tokenForUserId(user_id)
            method = '/AUTH-RSS?token={0}'.format(token)
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return context_state.object_url() + method


class AuthRSSView(BrowserView):
    """The RSS feed depending on the token
    """
    def __call__(self, *args, **kwargs):
        """Runs the view
        """
        token = self.request.form.get('token', 'invalid-token')
        with GrantPrivilegesForToken(token, self.context, self.request) as sm:
            feed = self.context.RSS()
        return feed

