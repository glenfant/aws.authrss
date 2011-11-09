# -*- coding: utf-8 -*-
# $Id$
"""Misc utilities for aws.authrss"""

from zope.component import getUtility
from AccessControl.SecurityManagement import (
    getSecurityManager, setSecurityManager, newSecurityManager
    )

from interfaces import ITokensManager


class GrantPrivilegesForToken(object):
    """A context manager that grants temporarily (roles, groups) for the user
    that has a token
    """
    def __init__(self, token, request):
        self.token = token
        self.request = request
        return

    def __enter__(self):
        """Grant privileges of the user who has the token
        """
        self.real_sm = getSecurityManager()
        tokens_bucket = getUtility(ITokensManager)
        user = tokens_bucket.memberForToken(self.token)
        newSecurityManager(self.request, user)
        return getSecurityManager()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Back to former security context
        """
        setSecurityManager(self.real_sm)

        # False: Re-raises exceptions that occured in the "with" block
        return False
