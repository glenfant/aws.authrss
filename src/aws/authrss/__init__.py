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
