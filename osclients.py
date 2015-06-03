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
from novaclient import client as novaclient
from cinderclient.v2 import client as cinderclient
from glanceclient import client as glanceclient


_session_v2 = None
_session_v3 = None
_saved_session_v2 = None
_saved_session_v3 = None
__username = None
__password = None
__tenant = None


def set_credential(username, password, tenant):
    global __username, __password, __tenant
    global _session_v2, _session_v3
    __username = username
    __password = password
    __tenant = tenant
    # clear sessions
    if _session_v2:
        _session_v2.invalidate()
        _session_v2 = None
    if _session_v3:
        _session_v3.invalidate()
        _session_v3 = None

def preserve_session():
    global _session_v2, _session_v3
    global _saved_session_v2, _saved_session_v3

    _saved_session_v2 = _session_v2
    _saved_session_v3 = _session_v3
    _session_v2 = None
    _session_v3 = None 

def restore_session():
    global _session_v2, _session_v3
    global _saved_session_v2, _saved_session_v3

    if _session_v2 and _session_v2 != _saved_session_v2:
        _session_v2.invalidate()
    if _session_v3 and _session_v3 != _saved_session_v3:
        _session_v3.invalidate()
    _session_v2 = _saved_session_v2
    _session_v3 = _saved_session_v3 
        
def get_session():
    return get_session_v3()


def get_session_v2():
    global _session_v2
    if _session_v2:
        return _session_v2

    auth_url = env['OS_AUTH_URL']
    if auth_url.endswith('/v3/'):
        auth_url = auth_url[0:-2] + '2.0'
    elif auth_url.endswith('/v3'):
        auth_url = auth_url[0:-1] + '2.0'

    print auth_url
    if __username and __password and __tenant:
        auth = v2.Password(
            auth_url=auth_url,
            username=__username,
            password=__password,
            tenant_name=__tenant)
    else:
        auth = v2.Password(
            auth_url=auth_url,
            username=env['OS_USERNAME'],
            password=env['OS_PASSWORD'],
            tenant_name=env['OS_TENANT_NAME'])
    _session_v2 = session.Session(auth=auth)
    return _session_v2


def get_session_v3():
    global _session_v3
    if _session_v3:
        return _session_v3

    auth_url = env['OS_AUTH_URL']
    if auth_url.endswith('/v2.0/'):
        auth_url = auth_url[0:-4] + '3'
    elif auth_url.endswith('/v2.0'):
        auth_url = auth_url[0:-3] + '3'

    if __username and __password and __tenant:
        auth = v3.Password(
            auth_url=auth_url,
            username=__username,
            password=__password,
            project_name=__tenant,
            project_domain_name='default', user_domain_name='default')
    else:
        auth = v3.Password(
            auth_url=auth_url,
            username=env['OS_USERNAME'],
            password=env['OS_PASSWORD'],
            project_name=env['OS_TENANT_NAME'],
            project_domain_name='default', user_domain_name='default')
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
        2, region_name=env['OS_REGION_NAME'], session=get_session())


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


def get_keystoneclientv2():
    session = get_session_v2()
    return keystonev2.Client(session=session)


def get_keystoneclientv3():
    session = get_session_v3()
    return keystonev3.Client(session=session)

def get_keystoneclient():
    return get_keystoneclientv3()

