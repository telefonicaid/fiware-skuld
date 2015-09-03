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
# TrialUserManagement settings.
__author__ = 'fla'

LOGGING_PATH = u'/var/log/fiware-trialusermanagement'
TRIAL_ROLE_ID = "7698be72802342cdb2a78f89aa55d8ac"
BASIC_ROLE_ID = "0bcb7fa6e85046cb9e89ded5656b192b"
KEYSTONE_ENDPOINT = "http://cloud.lab.fiware.org:4730/"
HORIZON_ENDPOINT = "https://130.206.84.7/"
TRUSTEE = "e.fiware4@telefonica.com"
MAX_NUMBER_OF_DAYS = 14  # days
TRUSTID_VALIDITY = 36000 # seconds
DONT_DELETE_DOMAINS = set((
   'create-net.org', 'telefonica.com', 'man.poznan.pl', 'wigner.mta.hu',
   'gatv.ssr.upm.es', 'thalesgroup.com', 'atos.net', 'uth.gr', 'bth.se',
   'iminds.be', 'intec.ugent.be', 'neuropublic.gr', 'zhaw.ch', 'tid.es',
   'it-innovation.soton.ac.uk', 'cesnet.cz', 'rt.cesnet.cz', 'rt3.cesnet.cz',
   'fokus.fraunhofer.de'))

