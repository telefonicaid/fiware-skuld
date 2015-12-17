# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
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

__author__ = 'gjp'

from os import environ
from unittest import TestCase
from skuld.openstackmap import OpenStackMap
from mock import patch, MagicMock
from collections import defaultdict
from requests import Response
from httplib import OK
from tests_constants import UNIT_TEST_RESOURCES_FOLDER, LIST_SERVERS_RESPONSE_FILE, LIST_VOLUMES_RESPONSE_FILE, \
    LIST_SNAPSHOTS_RESPONSE_FILE, LIST_ROLES_RESPONSE_FILE, LIST_BACKUPS_RESPONSE_FILE, LIST_USERS_RESPONSE_FILE, \
LIST_PROJECTS_RESPONSE_FILE, LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE, GET_USER_RESPONSE_FILE

import os


class MySessionMock(MagicMock):
    # Mock of a keystone Session

    def get_endpoint(self, auth, **kwargs):

        endpoint = "http://cloud.host.fi-ware.org:4731/v2.0"
        return endpoint

    def get_access(self, session):

        service2 = {u'endpoints': [{u'url': u'http://83.26.10.2:4730/v3/',
                                    u'interface': u'public', u'region': u'Spain2',
                                    u'id': u'00000000000000000000000000000002'},
                                   {u'url': u'http://172.0.0.1:4731/v3/', u'interface': u'administator',
                                    u'region': u'Spain2', u'id': u'00000000000000000000000000000001'}],
                                    u'type': u'identity', u'id': u'00000000000000000000000000000045'}

        d = defaultdict(list)
        d['catalog'].append(service2)

        return d

    def request(self, url, method, **kwargs):

        resp = Response()

        if url == '/servers/detail?all_tenants=1':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_SERVERS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/volumes/detail?all_tenants=1':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_VOLUMES_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/snapshots/detail?all_tenants=1':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_SNAPSHOTS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/backups/detail':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_BACKUPS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/roles':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLES_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/users' or url == '/users?name=user':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/users/00000000000000000000000000000001':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + GET_USER_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/projects':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_PROJECTS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        elif url == '/role_assignments':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        return resp


class TestOpenstackMap(TestCase):

    mock_session = MySessionMock()

    def setUp(self):
        self.OS_AUTH_URL = 'http://cloud.host.fi-ware.org:4731/v2.0'
        self.OS_USERNAME = 'user'
        self.OS_PASSWORD = 'password'
        self.OS_TENANT_NAME = 'user cloud'
        self.OS_TENANT_ID = '00000000000000000000000000000001'
        self.OS_REGION_NAME = 'Spain2'
        self.OS_TRUST_ID = ''
        self.OS_KEYSTONE_ADMIN_ENDPOINT = 'http://cloud.lab.fiware.org:4730'

        environ.setdefault('OS_AUTH_URL', self.OS_AUTH_URL)
        environ.setdefault('OS_USERNAME', self.OS_USERNAME)
        environ.setdefault('OS_PASSWORD', self.OS_PASSWORD)
        environ.setdefault('OS_TENANT_NAME', self.OS_TENANT_NAME)
        environ.setdefault('OS_TENANT_ID', self.OS_TENANT_ID)
        environ.setdefault('OS_REGION_NAME', self.OS_REGION_NAME)
        environ.setdefault('OS_TRUST_ID', self.OS_TRUST_ID)

    def tearDown(self):
        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_implement_openstackmap(self, mock_exists, mock_os):
        """test_implement_openstackmap check that we could build an empty map from the resources (VMs, networks, images,
        volumes, users, tenants, roles...) in an OpenStack infrastructure."""
        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(region=self.OS_REGION_NAME, auto_load=False)
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)

    def test_implement_openstackmap_without_region_name(self):
        """test_implement_openstackmap_without_region_name check that we could not build an empty map without providing
        a region Name."""

        del os.environ['OS_REGION_NAME']

        with self.assertRaises(Exception):
            OpenStackMap(auth_url=self.OS_AUTH_URL, auto_load=False)

    @patch('utils.osclients.session', mock_session)
    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_implement_openstackmap_with_keystone_admin_endpoint(self, mock_exists, mock_os):
        """test_implement_openstackmap_with_keystone_admin_endpoint check that we could build an empty map from the
         resources providing a keystone admin endpoint environment variable."""

        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(auto_load=False)
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)

    @patch('utils.osclients.session', mock_session)
    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_load_nova(self, mock_exists, mock_os):
        """test_load_nova check that we could build an empty map from nova resources."""

        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.NO_CACHE_OBJECTS)

        openstackmap.load_nova()
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)

    @patch('utils.osclients.session', mock_session)
    def test_load_nova2(self):
        """test_load_nova check that we could build a map from nova resources using Direct_objects directive."""

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_nova()
        self.assertIsNotNone(openstackmap)

    @patch('utils.osclients.session', mock_session)
    def test_load_cinder(self):
        """test_load_cinder check that we could build a map from cinder resources using Direct_objects directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_cinder()
        self.assertIsNotNone(openstackmap)

    @patch('utils.osclients.session', mock_session)
    def test_load_keystone(self):
        """test_load_keystone check that we could build a map from keystone resources using Direct_objects directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_keystone()
        self.assertIsNotNone(openstackmap)
