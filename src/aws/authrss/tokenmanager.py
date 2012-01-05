# -*- coding: utf-8 -*-
# $Id$
"""The default tokens manager"""

from zope.interface import implements
from zope.component import getUtility
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from plone.uuid.interfaces import IUUIDGenerator

from interfaces import ITokenManager


class DefaultTokenManager(Persistent):
    """Tokens manager persistent utility (per site)
    """
    implements(ITokenManager)

    def __init__(self):
        # {token: user id, ...}
        self._token2uid = OOBTree()
        # {user id: token, ...}
        self._uid2token = OOBTree()
        return

    def userIdForToken(self, token):
        """See ITokensManager
        """
        if token in self._token2uid:
            return self._token2uid[token]
        return

    def tokenForUserId(self, user_id):
        """See ITokensManager
        """
        if user_id in self._uid2token:
            return self._uid2token[user_id]

        # We'll make a token for this new user id
        return self.resetToken(user_id)

    def resetToken(self, user_id):
        """See ITokensManager
        """
        generator = getUtility(IUUIDGenerator)
        token = generator()
        self._token2uid[token] = user_id
        self._uid2token[user_id] = token
        return token

    def pruneUserId(self, user_id):
        """See ITokensManager
        """
        token = self._uid2token[user_id]
        del self._uid2token[user_id]
        del self._token2uid[token]
        return

    def knownUserIds(self):
        """See ITokensManager
        """
        for user_id in self._uid2token.keys():
            yield user_id
