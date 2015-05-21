#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
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
author = 'chema'

import osclients

"""This functions obtains information about the endpoints, but using
   the information included in the credential, instead of asking
   directly by services and the endpoints. This is more efficient and
   don't requiere access to admin server."""


def get_catalog():
    session = osclients.get_session()
    return session.auth.get_access(session)['catalog']


def get_endpoints(service_type):
    """Endpoinds is a list of dictionaries, with url, region,
       interface (private, public, admin) and other fields"""
    for service in get_catalog():
        if service['type'] == service_type:
            return service['endpoints']


def get_regions(service_type):
    endpoints = get_endpoints(service_type)
    regions = set()
    for endpoint in endpoints:
        regions.add(endpoint['region'])
    return regions
