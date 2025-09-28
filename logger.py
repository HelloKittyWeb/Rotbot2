# -*- coding: utf-8 -*-
import os
import sys

import logging
from logging.handlers import RotatingFileHandler
import constant
import config

os.makedirs(constant.logs_dir, exist_ok=True)
logger = logging.getLogger('main')
if config.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.logs_dir, 'log.txt'), maxBytes=10000000,
                                              backupCount=1, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)
_form = "[%(asctime)s] [%(levelname)8s] (%(filename)s:%(lineno)s)--- %(message)s"
rotate.setFormatter(logging.Formatter(_form))
consoleHandler.setFormatter(logging.Formatter(_form))
logger.addHandler(rotate)
logger.addHandler(consoleHandler)
