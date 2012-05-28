# -*- coding: utf-8 -*-
# $Id$
"""Views (z3) for aws.authrss"""
try:
    import simplejson as json
except ImportError:
    import json
from zope.component import getMultiAdapter, getUtility
from Products.Five import BrowserView
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction
from ZTUtils import make_query

from aws.authrss import aws_authrss_messagefactory as _
from aws.authrss.interfaces import ITokenManager
from aws.authrss.utils import GrantPrivilegesForToken, AuthRSSViewMixin


class RSSLinkView(BrowserView, AuthRSSViewMixin):
    """Builds the link for authenticated RSS
    """
    def __call__(self, *args, **kwargs):
        """Runs the view
        """
        return self.authRSSFolderishLink()


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


class PersonalTokenView(BrowserView, AuthRSSViewMixin):
    """The user may view/change his token from here
    """
    def __init__(self, *args, **kwargs):
        super(PersonalTokenView, self).__init__(*args, **kwargs)

        # Hiding content tabs and portlets
        request_set = self.request.set
        request_set('disable_border', 1)
        request_set('disable_plone.leftcolumn', 1)
        request_set('disable_plone.rightcolumn', 1)
        return

    def tokenValue(self):
        """Token value for UI
        """
        token = self.tokenForThisUser()
        if token is None:
            token = _(u'invalid_token', default=u"Invalid token")
        return token


class KSSTokensUtils(PloneKSSView, AuthRSSViewMixin):
    """KSS actions handler
    """
    @kssaction
    def resetToken(self):
        """Reset the user's token
        """
        if self.isUserAnonymous():
            return

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        user_id = portal_state.member().getId()
        token_mgr = getUtility(ITokenManager)
        new_token = token_mgr.resetToken(user_id)
        core_cs = self.getCommandSet('core')
        core_cs.setAttribute('#aws-authrss-token-value', 'value', new_token)
        plone_cs = self.getCommandSet('plone')
        plone_cs.issuePortalMessage(
            _(u'msg_token_changed',
              default=u"Your RSS token has been changed")
              )
        return

    @kssaction
    def purgeTokens(self):
        """Remove the tokens of unknown or gone users
        """
        pruned = 0
        plone_tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        mtool = plone_tools.membership()
        token_mgr = getUtility(ITokenManager)
        for user_id in token_mgr.knownUserIds():
            if mtool.getMemberById(user_id) is None:
                token_mgr.pruneUserId(user_id)
                pruned += 1
        plone_cs= self.getCommandSet('plone')
        message = _(
            u'msg_pruned_users',
            default=u"${pruned} unknown user(s) have been removed from RSS tokens registry",
            mapping={u'pruned': str(pruned)}
            )
        plone_cs.issuePortalMessage(message)
        return


class ControlPanelView(BrowserView):
    """Control panel
    """
    # Just a placeholder for future features.
    pass

###
# Search results related resources
# Note that this is somehow ugly but there's no other way to do this
###

class SearchPageModifierEnabler(BrowserView):
    def __call__(self, *args, **kwargs):
        # Are we on the "search" template (results)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return self.request.URL.startswith(portal_state.portal_url() + '/search')


AUTH_SEARCH_RSS_JS_TPL = """\
// Tweaking the links to RSS
$(function() {{
  var rss_url = {0};
  // Link in the header
  $('link[type="application/rss+xml"]').attr('href', rss_url);
  // Link in the results
  $('a[class="link-feed"]').attr('href', rss_url);
}});
"""

class SearchPageModifierJS(BrowserView, AuthRSSViewMixin):
    """Provides resources for changing links into the search results page
    """
    def __call__(self):
        """Make the user specific JS and tweaks the response accordingly
        """
        request = self.request
        if False: # This JS bunch is actually rendered inline, so we don't need this
            # Never cache this, even if distributed through squid/varnish
            response_header = request.RESPONSE.setHeader
            response_header(
                'Cache-Control',
                'no-cache, no-store, max-age=0, private, must-revalidate, pre-check=0, post-check=0'
                )
            response_header('Content-Type', 'application/javascript')

        # Let's make a JS response
        # Note that the user is authenticated at this step and has necessarily a token
        token = self.tokenForThisUser()
        context_state = getMultiAdapter((self.context, request), name=u'plone_context_state')
        context_url = context_state.object_url()
        query = make_query(self.request.form, token=token)
        rss_url = context_url + '/AUTH-SEARCH-RSS?' + query
        return AUTH_SEARCH_RSS_JS_TPL.format(json.dumps(rss_url))


class AuthSearchRSSView(BrowserView):
    """RSS for search results
    """
    def __call__(self, *args, **kwargs):
        """Runs the view
        """
        token = self.request.form.get('token', 'invalid-token')
        with GrantPrivilegesForToken(token, self.context, self.request) as sm:
            feed = self.context.search_rss()
        return feed

