from aws.authrss import aws_authrss_messagefactory as _
from aws.authrss.interfaces import ITokenManager
from aws.authrss.utils import AuthRSSViewMixin
from aws.authrss.utils import GrantPrivilegesForToken
from plone.app.layout.viewlets import ViewletBase
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from ZTUtils import make_query

import json


class RSSLinkView(BrowserView, AuthRSSViewMixin):
    """Builds the link for authenticated RSS"""

    def __call__(self, *args, **kwargs):
        """Runs the view"""
        return self.authRSSFolderishLink()


class AuthRSSView(BrowserView):
    """The RSS feed depending on the token"""

    def __call__(self, *args, **kwargs):
        """Runs the view"""
        token = self.request.form.get("token", "invalid-token")
        with GrantPrivilegesForToken(token, self.context, self.request):
            feed = self.context.restrictedTraverse("RSS")()
        return feed


class PersonalTokenView(BrowserView, AuthRSSViewMixin):
    """The user may view/change his token from here"""

    def tokenValue(self):
        """Token value for UI"""
        token = self.tokenForThisUser()
        if token is None:
            token = _("invalid_token", default="Invalid token")
        return token


class AjaxTokensUtils(BrowserView, AuthRSSViewMixin):
    """Ajax actions handler"""

    def resetToken(self):
        """Reset the user's token"""
        if self.isUserAnonymous():
            return

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        user_id = portal_state.member().getId()
        token_mgr = getUtility(ITokenManager)
        new_token = token_mgr.resetToken(user_id)

        return json.dumps(
            {
                "success": True,
                "message": translate(
                    _("msg_token_changed", default="Your RSS token has been changed"),
                    context=self.request,
                ),
                "token": new_token,
            }
        )

    def purgeTokens(self):
        """Remove the tokens of unknown or gone users"""
        pruned = 0
        plone_tools = getMultiAdapter((self.context, self.request), name="plone_tools")
        mtool = plone_tools.membership()
        token_mgr = getUtility(ITokenManager)
        for user_id in token_mgr.knownUserIds():
            if mtool.getMemberById(user_id) is None:
                token_mgr.pruneUserId(user_id)
                pruned += 1

        message = _(
            "msg_pruned_users",
            default="${pruned} unknown user(s) have been removed from RSS tokens registry",
            mapping={"pruned": str(pruned)},
        )
        return json.dumps(
            {
                "success": True,
                "message": translate(message, context=self.request),
            }
        )


class ControlPanelView(BrowserView):
    """Control panel"""

    # Just a placeholder for future features.
    pass


###
# Search results related resources
# Note that this is somehow ugly but there's no other way to do this
###

AUTH_SEARCH_RSS_JS_TPL = """\
<script>
// Tweaking the links to RSS
$(function() {{
  var rss_url = {0};
  // Link in the header
  $('link[type="application/rss+xml"]').attr('href', rss_url);
  // Link in the results
  $('a[class="link-feed"]').attr('href', rss_url);
}});
</script>
"""


class SearchPageModifierJS(ViewletBase, AuthRSSViewMixin):
    """Provides resources for changing links into the search results page"""

    def index(self):
        """Make the user specific JS and tweaks the response accordingly"""
        if self.isUserAnonymous():
            return ""

        # Are we on the "search" view (results)
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        if not self.request.URL.startswith(
            portal_state.portal_url() + "/search"
        ) and not self.request.URL.startswith(portal_state.portal_url() + "/@@search"):
            return ""

        request = self.request
        token = self.tokenForThisUser()
        context_state = getMultiAdapter(
            (self.context, request), name="plone_context_state"
        )
        context_url = context_state.object_url()
        query = make_query(self.request.form, token=token)
        rss_url = context_url + "/AUTH-SEARCH-RSS?" + query
        return AUTH_SEARCH_RSS_JS_TPL.format(json.dumps(rss_url))


class AuthSearchRSSView(BrowserView):
    """RSS for search results"""

    def __call__(self, *args, **kwargs):
        """Runs the view"""

        token = self.request.form.get("token", "invalid-token")
        with GrantPrivilegesForToken(token, self.context, self.request):
            feed = self.context.restrictedTraverse("search_rss")()
        return feed
