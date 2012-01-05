# -*- coding: utf-8 -*-
# $Id$
"""Views (z3) for aws.authrss"""

from zope.component import getMultiAdapter, getUtility
from Products.Five import BrowserView
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction

from aws.authrss import aws_authrss_messagefactory as _
from aws.authrss.interfaces import ITokenManager
from aws.authrss.utils import GrantPrivilegesForToken


class AuthRSSViewMixin(object):
    """Mixin class for some utilities common to various views
    """
    def tokenForThisUser(self):
        """Token for authenticated user or None for anonymous
        """
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if not portal_state.anonymous():

            # We have an authenticated member
            user_id = portal_state.member().getId()
            token_mgr = getUtility(ITokenManager)
            return token_mgr.tokenForUserId(user_id)
        return None


class RSSLinkView(BrowserView, AuthRSSViewMixin):
    """Builds the link for authenticated RSS
    """
    def __call__(self, *args, **kwargs):
        """Runs the view
        """
        token = self.tokenForThisUser()
        method = '/AUTH-RSS?token={0}'.format(token) if token is not None else '/RSS'
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


class PersonalTokenView(BrowserView, AuthRSSViewMixin):
    """The user may view/change his token from here
    """
    def __init__(self, *args, **kwargs):
        super(PersonalTokenView, self).__init__(*args, **kwargs)

        # Hiding content tabs and portlets
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        return

    def tokenValue(self):
        """Token value for UI
        """
        token = self.tokenForThisUser()
        if token is None:
            token = _(u'invalid_token', default=u"Invalid token")
        return token


class KSSTokensUtils(PloneKSSView):
    """KSS actions handler
    """
    @kssaction
    def resetToken(self):
        """Reset the user's token
        """
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if portal_state.anonymous():
            return

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
    pass
