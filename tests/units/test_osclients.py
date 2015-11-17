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
from utils.osclients import OpenStackClients
import cinderclient.v2.client
import neutronclient.v2_0.client
import novaclient.v2.client


class TestOSClients(TestCase):

    def setUp(self):
        OS_AUTH_URL = 'http://host.com:4731/v3'
        OS_USERNAME = 'user'
        OS_PASSWORD = 'password'
        OS_TENANT_NAME = 'user cloud'
        OS_TENANT_ID = ''
        OS_REGION_NAME = 'Spain2'
        OS_TRUST_ID = ''

        environ.setdefault('OS_AUTH_URL', OS_AUTH_URL)
        environ.setdefault('OS_USERNAME', OS_USERNAME)
        environ.setdefault('OS_PASSWORD', OS_PASSWORD)
        environ.setdefault('OS_TENANT_NAME', OS_TENANT_NAME)
        environ.setdefault('OS_TENANT_ID', OS_TENANT_ID)
        environ.setdefault('OS_REGION_NAME', OS_REGION_NAME)
        environ.setdefault('OS_TRUST_ID', OS_TRUST_ID)

    def test_implement_client(self):
        """test_implement_client check that we could implement an empty client."""

        osclients = OpenStackClients()
        self.assertIsNotNone(osclients)

    def test_implement_client_with_unknown_module(self):
        """test_implement_client_with_unknown_module check that we could not implement an empty client,
        raising an exception."""

        try:
            osclients = OpenStackClients(modules="fakeOpenstackModule")
        except Exception as ex:
            self.assertRaises(ex)

    def test_implement_client_with_all_modules(self):
        """test_implement_client_with_all_modules check that we could not implement an empty client,
        with all modules and a given auth_url"""

        OS_AUTH_URL = 'http://host.com:4731/v3'

        osclients = OpenStackClients(modules="all", auth_url=OS_AUTH_URL)
        self.assertIsNotNone(osclients)

    def test_implement_client_with_selected_module(self):
        """test_implement_client_with_selected_module check that we could not implement an empty client, with selected
         modules (keystone and cinder)"""
        selected_modules = "keystone,cinder,"

        osclients = OpenStackClients(modules=selected_modules)

        self.assertIsNotNone(osclients)

    def test_implement_client_with_env(self):
        """test_implement_client_with_env check that we could implement a client with data from the OS environment."""

        osclients = OpenStackClients()

        self.assertIsNotNone(osclients)

    def test_get_cinderclient(self):
        """test_get_cinderclient check that we could retrieve a Session client to work with cinder"""
        osclients = OpenStackClients(modules="cinder")
        cinderClient = osclients.get_cinderclient()

        self.assertIsInstance(cinderClient, cinderclient.v2.client.Client)

    def test_get_cinderclient_unknown_module(self):
        """test_get_cinderclient_unknown_module check that we could not retrieve a Session client to work with cinder if
        there is no modules defined"""
        try:
            osclients = OpenStackClients(modules="")
            cinderClient = osclients.get_cinderclient()
        except Exception as ex:
            self.assertRaises(ex)

    def test_get_neutronclient_with_all_modules(self):
        """test_get_neutronclient_with_all_modules check that we could retrieve a Session client to work with neutron if
        osclients is created with all modules"""

        osclients = OpenStackClients(modules="auto")
        neutronClient = osclients.get_neutronclient()

        self.assertIsInstance(neutronClient, neutronclient.v2_0.client.Client)

    def test_get_novaclient(self):
        """test_get_novaclient check that we could retrieve a Session client to work with nova"""
        osclients = OpenStackClients(modules="nova")
        novaClient = osclients.get_novaclient()

        self.assertIsInstance(novaClient, novaclient.v2.client.Client)
