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
# Skuld settings.
__author__ = 'fla'

LOGGING_PATH = u'/var/log/fiware-skuld'
KEYSTONE_ENDPOINT = "http://{KEYSTONE_ENDPOINT}/"
HORIZON_ENDPOINT = "https://{HORIZON_ENDPOINT}/"
TRUSTEE = "idm"
TRUSTEE_PASSWORD = ""
TRIAL_MAX_NUMBER_OF_DAYS = 14  # days
COMMUNITY_MAX_NUMBER_OF_DAYS = 100  # days
NOTIFY_BEFORE_TRIAL_EXPIRED = 7  # days
NOTIFY_BEFORE_COMMUNITY_EXPIRED = 30  # days
STOP_BEFORE_DELETE = 0  # days
TRUSTID_VALIDITY = 36000  # seconds
TRIAL_ROLE_ID = "trial_id"
COMMUNITY_ROLE_ID = "community_id"
BASIC_ROLE_ID = "basic_id"
ADMIN_ROLE_ID = "admin_id"
DONT_DELETE_DOMAINS = ([
    'create-net.org', 'telefonica.com', 'man.poznan.pl', 'wigner.mta.hu', 'gatv.ssr.upm.es', 'thalesgroup.com',
    'atos.net', 'uth.gr', 'bth.se', 'iminds.be', 'intec.ugent.be', 'neuropublic.gr', 'zhaw.ch', 'tid.es',
    'it-innovation.soton.ac.uk', 'cesnet.cz', 'rt.cesnet.cz', 'rt3.cesnet.cz', 'fokus.fraunhofer.de'])
