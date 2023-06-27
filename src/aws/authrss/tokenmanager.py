"""The default tokens manager"""

from aws.authrss.interfaces import ITokenManager
from persistent import Persistent
from persistent.dict import PersistentDict
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility
from zope.interface import implementer


@implementer(ITokenManager)
class DefaultTokenManager(Persistent):
    """Tokens manager persistent utility (per site)"""

    def __init__(self):
        self.clear()

    def clear(self):
        # {token: user id, ...}
        self._token2uid = PersistentDict()
        # {user id: token, ...}
        self._uid2token = PersistentDict()

    def userIdForToken(self, token):
        """See ITokensManager"""
        return self._token2uid.get(token, None)

    def tokenForUserId(self, user_id):
        """See ITokensManager"""
        if user_id in self._uid2token.keys():
            return self._uid2token[user_id]

        # We'll make a token for this new user id
        return self.resetToken(user_id)

    def resetToken(self, user_id):
        """See ITokensManager"""
        old_token = self._uid2token.get(user_id, None)
        if old_token is not None:
            del self._token2uid[old_token]

        generator = getUtility(IUUIDGenerator)
        token = generator()
        self._token2uid[token] = user_id
        self._uid2token[user_id] = token
        return token

    def pruneUserId(self, user_id):
        """See ITokensManager"""
        token = self._uid2token[user_id]
        del self._uid2token[user_id]
        del self._token2uid[token]

    def knownUserIds(self):
        """See ITokensManager"""
        yield from self._uid2token.keys()
