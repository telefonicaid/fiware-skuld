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
import unittest
from mock import MagicMock

from fiwareskuld.nova_resources import NovaResources

__author__ = 'chema'


class TestNovaResourcesContructor(unittest.TestCase):
    """class for testing the constructor of NovaResources"""
    def test_constructor(self):
        """test constructor and self attributes after the call"""
        config = {'get_novaclient.return_value': 'fake_nova_client',
                  'get_session.return_value.get_project_id.return_value': 'id'}
        osclients = MagicMock(**config)
        nova_resources = NovaResources(osclients)
        self.assertEquals(nova_resources.osclients, osclients)
        self.assertEquals(nova_resources.novaclient, 'fake_nova_client')
        self.assertEquals(nova_resources.tenant_id, 'id')


class TestNovaResources(unittest.TestCase):
    """class for testing the methods of NovaResources"""
    def setUp(self):
        """create and object and fill the fields with mocks"""
        osclients = MagicMock()
        self.nova_resources = NovaResources(osclients)
        self.nova_resources.novaclient = MagicMock(name='novaclient')
        self.nova_resources.tenant_id = 'tenant_id'

    def test_on_region_changed(self):
        """test method on_region_changed. Check that a new client is got"""
        old_client = self.nova_resources.novaclient
        self.nova_resources.on_region_changed()
        # check than nova client object has changed
        new_client = self.nova_resources.novaclient
        self.assertNotEquals(old_client, new_client)

    def prepare_vms(self, mock):
        """prepare mock to do operations with VMS
        There are 4 VMs, all but the one are in ACTIVE state"""
        vms = list()
        for i in range(3):
            vms.append(MagicMock(id=i, user_id='userid', status='ACTIVE',
                                 tenant_id=self.nova_resources.tenant_id))
        vms.append(MagicMock(id=3, user_id='userid', status='OTHER',
                             tenant_id=self.nova_resources.tenant_id))
        config = {'servers.list.return_value': vms}
        mock.configure_mock(**config)
        return vms

    def test_get_tenant_vms(self):
        """test get_tenant_vms method. Check id, user_id and status of each
        VM"""
        self.prepare_vms(self.nova_resources.novaclient)
        result = self.nova_resources.get_tenant_vms()
        for i in range(3):
            self.assertEquals(result[i][0], i)
            self.assertEquals(result[i][1], 'userid')
            self.assertEquals(result[i][2], 'ACTIVE')
        self.assertEquals(result[3][0], 3)
        self.assertEquals(result[3][1], 'userid')
        self.assertEquals(result[3][2], 'OTHER')

    def test_stop_tenant_vms(self):
        """test stop_tenant_vms. If checks that the stop method of the mock
        is called for all the VMs in ACTIVE state"""
        vms = self.prepare_vms(self.nova_resources.novaclient)
        count = self.nova_resources.stop_tenant_vms()
        self.assertEquals(count, 3)
        for i in range(3):
            self.assertTrue(vms[i].stop.called)
        self.assertFalse(vms[3].stop.called)

    def test_delete_tenant_vms(self):
        """Check that the delete method of each VM is invoked"""
        config = {'servers.list.return_value': []}
        self.nova_resources.novaclient.configure_mock(**config)
        self.nova_resources.delete_tenant_vms()

    def prepare_keypairs(self, mock):
        """create mock to check operatios with keypairs"""
        keypairs = list()
        for i in range(3):
            keypairs.append(MagicMock(id=i))
        config = {'keypairs.list.return_value': keypairs}
        mock.configure_mock(**config)
        return keypairs

    def test_get_user_keypairs(self):
        """check that keypair list is obtained"""
        self.prepare_keypairs(self.nova_resources.novaclient)
        result = self.nova_resources.get_user_keypairs()
        for i in range(3):
            self.assertEquals(result[i], i)

    def test_delete_user_keypairs(self):
        """check that delete method is called for each keypair"""
        keypairs = self.prepare_keypairs(self.nova_resources.novaclient)
        self.nova_resources.delete_user_keypairs()
        for i in range(3):
            keypairs[i].delete.assert_called_once_with()

    def prepare_groups(self):
        """create 6 security groups to do tests. The first 4 groups have
        tenant_id == self.nova_resources.tenant_id. The 5th group also has
        that tenant_id, but has name == 'default'. Finally, the 6th group has
        a different tenant_id. This is because the default security group
        and the security group owned by other tenants should be ignored"""

        secgroups = list()
        for i in range(5):
            secgroup = MagicMock(tenant_id=self.nova_resources.tenant_id, id=i)
            secgroups.append(secgroup)
        secgroups[4].name = 'default'
        secgroups.append(MagicMock(tenant_id='other', id=5))
        return secgroups

    def test_get_tenant_security_groups(self):
        """check the code that get the security groups: check that filter
        the default group and the security groups of other tenants"""
        secgroups = self.prepare_groups()
        config = {'security_groups.list.return_value': secgroups}
        self.nova_resources.novaclient.configure_mock(**config)
        security_groups = self.nova_resources.get_tenant_security_groups()
        self.assertTrue(len(security_groups) == 4)
        for security_id in security_groups:
            self.assertTrue(security_id < 4)

    def test_delete_tenant_security_groups(self):
        """check that delete call is invoked in security groups with
        the same tenant_id than the object and that default is not deleted"""
        secgroups = self.prepare_groups()
        config = {'security_groups.findall.return_value': secgroups}
        self.nova_resources.novaclient.configure_mock(**config)
        self.nova_resources.delete_tenant_security_groups()
        for i in range(4):
            self.assertTrue(secgroups[i].delete.called)
        for i in range(4, 6):
            self.assertFalse(secgroups[i].delete.called)
