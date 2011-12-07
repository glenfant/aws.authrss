# -*- coding: utf-8 -*-
# $Id$
"""Misc utilities for aws.authrss"""

from zope.component import getUtility, getMultiAdapter
from AccessControl.SecurityManagement import (
    getSecurityManager, setSecurityManager, newSecurityManager
    )

from interfaces import ITokenManager
from aws.authrss import LOG


class GrantPrivilegesForToken(object):
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
        """Grant privileges of the user who has the token
        """
        self.real_sm = getSecurityManager()
        tokens_bucket = getUtility(ITokenManager)
        user_id = tokens_bucket.userIdForToken(self.token)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        pas = portal_state.portal().acl_users
        member = pas.getUserById(user_id)
        if member is not None:
            newSecurityManager(self.request, member)
        else:
            LOG.warning("No user for token %s, will be considered as anonymous", user_id)
        return getSecurityManager()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Back to former security context
        """
        setSecurityManager(self.real_sm)

        # False: Re-raises exceptions that occured in the "with" block
        return False
