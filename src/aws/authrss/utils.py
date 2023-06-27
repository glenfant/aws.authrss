"""Misc utilities for aws.authrss"""
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from aws.authrss import logger
from aws.authrss.interfaces import ITokenManager
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides


class GrantPrivilegesForToken:
    """A context manager that grants temporarily (roles, groups) for the user
    that has a token
    """

    def __init__(self, token, context, request=None):
        self.token = token
        self.context = context
        if request is None:
            self.request = context.REQUEST
        else:
            self.request = request
        return

    def __enter__(self):
        """Grant privileges of the user who has the token"""
        self.real_sm = getSecurityManager()
        tokens_bucket = getUtility(ITokenManager)
        user_id = tokens_bucket.userIdForToken(self.token)
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        pas = portal_state.portal().acl_users
        member = pas.getUserById(user_id)
        if member is not None:
            newSecurityManager(self.request, member)
        else:
            logger.info(
                "No user for token %s, will be considered as anonymous", user_id
            )
        return getSecurityManager()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Back to former security context"""
        setSecurityManager(self.real_sm)

        # False: Re-raises exceptions that occurred in the "with" block
        return False


class AuthRSSViewMixin:
    """Mixin class for some utilities common to various views
    May be inherited by a BrowserView or ViewletBase subclass
    """

    def isUserAnonymous(self):
        """(self speaking) Shortcut to the (noisy) usual method"""
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return portal_state.anonymous()

    def tokenForThisUser(self):
        """Token for authenticated user or None for anonymous"""
        if not self.isUserAnonymous():
            alsoProvides(self.request, IDisableCSRFProtection)
            # We have an authenticated member
            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            )
            user_id = portal_state.member().getId()
            token_mgr = getUtility(ITokenManager)
            return token_mgr.tokenForUserId(user_id)
        return None

    def authRSSFolderishLink(self):
        """URL of authenticated RSS for a folderish context"""
        token = self.tokenForThisUser()
        method = f"/AUTH-RSS?token={token}" if token is not None else "/RSS"
        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )
        if context_state.is_portal_root():
            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            )
            portal = portal_state.portal()
            return portal.absolute_url() + method

        return self.context.absolute_url() + method
