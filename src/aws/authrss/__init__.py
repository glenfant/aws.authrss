from zope.i18nmessageid import MessageFactory

import logging


PROJECT_NAME = "aws.authrss"

aws_authrss_messagefactory = MessageFactory(PROJECT_NAME)
logger = logging.getLogger(PROJECT_NAME)
