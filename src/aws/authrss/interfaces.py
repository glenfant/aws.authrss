# -*- coding: utf-8 -*-
# $Id$
"""Public interfaces of aws.authrss"""

from zope.interface import Interface


class IAuthRSSLayer(Interface):
    """Layer marker interface available when browsing Plone site where we are
    installed, using the profiles/default/browserlayer.xml
    """


class ITokenManager(Interface):
    """Tokens management utility
    """

    def userIdForToken(token):
        """The user id for a given token or None (anonymous).
        """

    def tokenForUserId(user_id):
        """The token for a member id. The token is generated and stored
        in a persistent backend if missing.
        """

    def resetToken(user_id):
        """Making a new token for either a new user or renewal at user request.
        And returns the token
        """

    def pruneUserId(user_id):
        """Remove the token for an user about to be removed
        """

    def knownUserIds():
        """An iterable over (or sequence of) registered user ids
        """
