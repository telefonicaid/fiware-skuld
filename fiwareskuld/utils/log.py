#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
from conf import settings
import logging
import os
from logging.handlers import RotatingFileHandler

__author__ = 'fla'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LOGFILE = 'fiware-skuld.log'

if not os.path.exists(settings.LOGGING_PATH):
    os.makedirs(settings.LOGGING_PATH)

log_handler = RotatingFileHandler(LOGFILE, maxBytes=1048576, backupCount=5)

formatter = logging.Formatter('%(asctime)s %(levelname)s Skuld [-]'
                              '%(message)s')
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


def _init_logger(logger, phase):
    log_handler = RotatingFileHandler(LOGFILE, maxBytes=1048576, backupCount=5)
    fmt = '%(asctime)s %(levelname)s {0} [-] %(message)s'.format(phase)
    formatter = logging.Formatter(fmt)
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)


def init_logs(phase):
    """Returns an initialized logger for the main program. Initializes also the
     loggers for other modules"""
    # logger = logging.getLogger(__name__)
    logger = logging.getLogger('__main__')
    # Complete this if the program has new modules
    _init_logger(logger, phase)
    _init_logger(logging.getLogger('skuld.user_resources'), phase)
    _init_logger(logging.getLogger('skuld.glance_resources'), phase)
    _init_logger(logging.getLogger('skuld.cinder_resources'), phase)
    _init_logger(logging.getLogger('skuld.nova_resources'), phase)
    _init_logger(logging.getLogger('skuld.neutron_resources'), phase)
    _init_logger(logging.getLogger('skuld.blueprint_resources'), phase)
    _init_logger(logging.getLogger('skuld.swift_resources'), phase)
    _init_logger(logging.getLogger('skuld.impersonate'), phase)
    _init_logger(logging.getLogger('utils.osclients'), phase)
    _init_logger(logging.getLogger('phase0b_notify_users'), phase)

    # init root logger, to show messages also in stderr
    logging.debug('start delete script')
    return logger
