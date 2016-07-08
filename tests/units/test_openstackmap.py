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


import os
from os import environ
from unittest import TestCase
from mock import patch, MagicMock
from collections import defaultdict
from requests import Response
from httplib import OK, NOT_FOUND
import tempfile
import cPickle as pickle
from tests_constants import UNIT_TEST_RESOURCES_FOLDER, LIST_SERVERS_RESPONSE_FILE, LIST_VOLUMES_RESPONSE_FILE, \
    LIST_SNAPSHOTS_RESPONSE_FILE, LIST_ROLES_RESPONSE_FILE, LIST_BACKUPS_RESPONSE_FILE, LIST_USERS_RESPONSE_FILE, \
    LIST_PROJECTS_RESPONSE_FILE, LIST_ROLE_ASSIGNMENTS_RESPONSE_FILE, GET_USER_RESPONSE_FILE, \
    LIST_USERS_RESPONSE_FILE4

from fiwareskuld.openstackmap import OpenStackMap

OS_TENANT_ID = '00000000000000000000000000000001'
OS_TENANT_ID2 = '00000000000000000000000000000002'


class MySessionBaseMock(MagicMock):
    # Mock of a keystone Session
    def get_endpoint(self, auth, **kwargs):

        endpoint = "http://cloud.host.fi-ware.org:4731/v2.0"
        return endpoint

    def get_access(self, session):

        service2 = {u'endpoints': [{u'url': u'http://83.26.10.2:4730/v3/',
                                    u'interface': u'public', u'region': u'Spain2',
                                    u'id': u'00000000000000000000000000000002'},
                                   {u'url': u'http://172.0.0.1:4731/v3/', u'interface': u'administator',
                                    u'region': u'Spain2', u'id': u'00000000000000000000000000000001'
                                    }
                                   ],
                    u'type': u'identity', u'id': u'00000000000000000000000000000045'}

        d = defaultdict(list)
        d['catalog'].append(service2)

        return d


class MySessionFakeMock(MySessionBaseMock):
    def request(self, url, method, **kwargs):

        resp = Response()

        if url == '/users':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE).read()
            resp.status_code = NOT_FOUND
            resp._content = json_data
        elif url == '/users/' + OS_TENANT_ID:
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + GET_USER_RESPONSE_FILE).read()
            resp.status_code = NOT_FOUND
            resp._content = json_data
            resp.reason = 'No data received'
        elif url == '/users/' + OS_TENANT_ID2:
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + GET_USER_RESPONSE_FILE).read()
            resp.status_code = OK
            resp._content = json_data

        return resp


class MySessionFakeMock2(MySessionBaseMock):
    def request(self, url, method, **kwargs):

        resp = Response()

        if url == '/users':
            json_data = open(UNIT_TEST_RESOURCES_FOLDER + LIST_USERS_RESPONSE_FILE4).read()
            resp.status_code = NOT_FOUND
            resp._content = json_data
        elif url == '/users/' + OS_TENANT_ID2:
            if method == 'GET':
                json_data = open(UNIT_TEST_RESOURCES_FOLDER + GET_USER_RESPONSE_FILE).read()
                resp.status_code = OK
                resp._content = json_data
            elif method == 'PATCH':
                json_data = open(UNIT_TEST_RESOURCES_FOLDER + GET_USER_RESPONSE_FILE).read()
                resp.status_code = NOT_FOUND
                resp._content = json_data
                resp.reason = 'No PATCH'

        return resp


class MySessionMock(MySessionBaseMock):
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

        elif url == '/users/' + OS_TENANT_ID:
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
        self.OS_TENANT_ID = OS_TENANT_ID
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

    @patch('fiwareskuld.utils.osclients.session', mock_session)
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

    @patch('fiwareskuld.utils.osclients.session', mock_session)
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

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_load_nova2(self):
        """test_load_nova check that we could build a map from nova resources using Direct_objects directive."""

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_nova()
        self.assertIsNotNone(openstackmap)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_load_cinder(self):
        """test_load_cinder check that we could build a map from cinder resources using Direct_objects directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_cinder()
        self.assertIsNotNone(openstackmap)

    @patch('fiwareskuld.utils.osclients.session', mock_session)
    def test_load_keystone(self):
        """test_load_keystone check that we could build a map from keystone resources using Direct_objects
        directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_keystone()
        self.assertIsNotNone(openstackmap)


class TestOpenstackMapCacheOnly(TestCase):
    keystone_objects = ['users', 'users_by_name', 'tenants', 'tenants_by_name', 'roles_a',
                        'filters', 'filters_by_project', 'roles', 'roles_by_user', 'roles_by_project']

    def setUp(self):
        """Create fake pickle objects to be used as cache"""
        self.tmpdir = tempfile.mkdtemp()
        os.mkdir(self.tmpdir + os.path.sep + 'keystone')
        os.mkdir(self.tmpdir + os.path.sep + 'region1')
        os.mkdir(self.tmpdir + os.path.sep + 'region2')
        sample_dict = {id: 'value1'}
        for resource in self.keystone_objects:
            with open(self.tmpdir + '/keystone/' + resource + '.pickle', 'wb') as f:
                pickle.dump(sample_dict, f, protocol=-1)

        for resource in OpenStackMap.resources_region:
            with open(self.tmpdir + '/region1/' + resource + '.pickle', 'wb') as f:
                pickle.dump(sample_dict, f, protocol=-1)

        with open(self.tmpdir + '/region2/vms.pickle', 'wb') as f:
            pickle.dump(sample_dict, f, protocol=-1)

        self.map = OpenStackMap(
            self.tmpdir, region='region1', auto_load=False, objects_strategy=OpenStackMap.USE_CACHE_OBJECTS_ONLY)

    def tearDown(self):
        for dir in os.listdir(self.tmpdir):
            for name in os.listdir(self.tmpdir + os.path.sep + dir):
                print self.tmpdir + os.path.sep + dir + os.path.sep + name
                os.unlink(self.tmpdir + os.path.sep + dir + os.path.sep + name)
        os.rmdir(self.tmpdir + '/keystone')
        os.rmdir(self.tmpdir + '/region1')
        os.rmdir(self.tmpdir + '/region2')
        os.rmdir(self.tmpdir)

    def test_load_all(self):
        """test the load_all method"""
        self.map.load_all()
        for resource in OpenStackMap.resources_region:
            data = getattr(self.map, resource)
            self.assertTrue(data)

        for resource in self.keystone_objects:
            data = getattr(self.map, resource)
            self.assertTrue(data)

    def test_load_nova_region2(self):
        """test the load_nova in region2"""
        self.map.change_region('region2', False)
        self.map.load_nova()
        self.assertTrue(self.map.vms)

    def test_load_all_region2(self):
        """test the load_all in region2 (is invoked by change_region)"""
        self.map.change_region('region2')
        self.assertTrue(self.map.vms)
        # region2 has vms, but not other resources as networks
        self.assertFalse(self.map.networks)

    def test_load_neutron_region2_failed(self):
        """test the load_neutron in region2: it must fail"""
        self.map.change_region('region2', False)
        with self.assertRaises(Exception):
            self.map.load_neutron()

    def test_preload_regions(self):
        """test the preload_regions method"""
        self.map.preload_regions()
        self.assertEquals(len(self.map.region_map), 2)
        self.assertTrue(self.map.region_map['region2']['vms'])
