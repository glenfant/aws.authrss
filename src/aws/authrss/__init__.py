# -*- extra stuff goes here -*-
"""aws.authrss package"""
from zope.i18nmessageid import MessageFactory
import logging

import config

aws_authrss_messagefactory = MessageFactory(config.PACKAGENAME)

LOG = logging.getLogger(config.PACKAGENAME)

__version__ = None

def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    # Setting the version
    import os
    from Products.CMFPlone.utils import versionTupleFromString
    global __version__

    version_txt_path = os.path.join(os.path.dirname(__file__), 'version.txt')
    version_txt = open(version_txt_path).read().strip()
    __version__ = versionTupleFromString(version_txt)
    LOG.info("version %s installed", version_txt)
    return
