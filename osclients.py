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

from os import environ as env

from keystoneclient.auth.identity import v2, v3
from keystoneclient import session
from keystoneclient.v2_0 import client as keystonev2
from keystoneclient.v3 import client as keystonev3

from neutronclient.v2_0 import client as neutronclient
import novaclient.v1_1.client as novaclient
from cinderclient.v2 import client as cinderclient
from glanceclient import client as glanceclient


_session = None
_session_v3 = None

def get_session():
    global _session
    if _session:
        return _session

    auth = v2.Password(
        auth_url=env['OS_AUTH_URL'],
        username=env['OS_USERNAME'],
        password=env['OS_PASSWORD'],
        tenant_name=env['OS_TENANT_NAME'])
    _session = session.Session(auth=auth)
    return _session

def get_session_v3():
    global _session_v3
    if _session_v3:
        return _session_v3

    auth = v3.Password(
        auth_url=env['OS_AUTH_URL'],
        user_id=env['OS_USERNAME'],
        password=env['OS_PASSWORD'],
        project_id=env['OS_TENANT_NAME'])
    _session_v3 = session.Session(auth=auth)
    return _session_v3

def get_neutronclient():
    region = None
    if 'OS_REGION_NAME' in env:
        region = env['OS_REGION_NAME']
    return neutronclient.Client(
        session=get_session(), region_name=region)

def get_novaclient():
    region = None
    if 'OS_REGION_NAME' in env:
        region = env['OS_REGION_NAME']
    return novaclient.Client(
        env['OS_USERNAME'], env['OS_PASSWORD'], env['OS_TENANT_NAME'],
        env['OS_AUTH_URL'], region_name=region,
        service_type='compute')
    # According to documentation, this should work,
    # return novaclient.Client(
    #    '2', region_name=env['OS_REGION_NAME'], session=get_session())

def get_cinderclient():
    region = None
    if 'OS_REGION_NAME' in env:
        region = env['OS_REGION_NAME']
    return cinderclient.Client(session=get_session(), region_name=region)

def get_glanceclient():
    session = get_session()
    token = session.get_token()
    region = None
    if 'OS_REGION_NAME' in env:
        region = env['OS_REGION_NAME']
    endpoint = session.get_endpoint(service_type='image', region_name=region)
    return glanceclient.Client(version='1', endpoint=endpoint, token=token)

def get_keystoneclient():
    session = get_session()
    return keystonev2.Client(session=session)

def get_keystoneclientv3():
    session = get_session_v3()
    return keystonev3.Client(session=session)