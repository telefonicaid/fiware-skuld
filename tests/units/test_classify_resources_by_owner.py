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
from mock import MagicMock, patch, call, ANY

from scripts.classify_resources_by_owners import ClassifyResources, hidden_set
from conf.settings import TRIAL_ROLE_ID, COMMUNITY_ROLE_ID, BASIC_ROLE_ID,\
    ADMIN_ROLE_ID

__author__ = 'chema'


class _DictAttr(dict):
    """dictionary that allows access as d['key'] and d.key"""
    def __init__(self):
        """constructor"""
        self.__dict__ = self
        dict.__init__(self, dict())


class TestClassifyResources(unittest.TestCase):

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def testConstructorBasic(self, mock):
        """check constructor without parameters"""
        classify = ClassifyResources('/fakedir')
        self.assertFalse(mock.return_value.preload_regions.called)
        self.assertTrue(mock.return_value.filters.values.called)
        self.assertTrue(mock.return_value.users.values.called)
        self.assertTrue(mock.return_value.tenants.keys.called)

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def testConstructorRegions(self, mock):
        """check constructor with a list of regions as parameter"""
        classify = ClassifyResources('/fakedir', ['region0', 'region1'])
        self.assertTrue(mock.return_value.preload_regions.called)
        self.assertTrue(mock.return_value.filters.values.called)
        self.assertTrue(mock.return_value.users.values.called)
        self.assertTrue(mock.return_value.tenants.keys.called)

    def init_filters(self, mock):
        """Method to configure in the mock the filters by region"""
        filters = list()
        # Put a more specific filter for region 0

        for i in range(4):
            filter = _DictAttr()
            filter.id = i
            filter['filters'] = {'region_id': 'region' + str(i)}
            filters.append(filter)
        # Clean the filter condition of one of the filters
        filters[3]['filters'] = None

        # Project (tenant) filters
        filters_by_project = dict()
        self.tenants_in_region0 = [
            'cpi_1', 'cpi_2', 'cpi_3', 'cpi_6', 'cpi_7', 'cpi_8', 'cpi_9'
            'dpi_1', 'dpi_7']
        self.tenants_in_region1 = [
            'cpi_1', 'cpi_2', 'cpi_4', 'cpi_5', 'cpi_7']

        for tenant in self.tenants_in_region0:
            filters_by_project[tenant] = [filters[0].id]
        for tenant in self.tenants_in_region1:
            if tenant in filters_by_project:
                filters_by_project[tenant].append(filters[1].id)
            else:
                filters_by_project[tenant] = [filters[1].id]

        config = {'return_value.filters.values.return_value': filters,
                  'return_value.filters_by_project': filters_by_project}
        mock.configure_mock(**config)

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def testConstructorFilter(self, mock):
        """test constructor providing filters in the mock"""
        self.init_filters(mock)
        classify = ClassifyResources('/fakedir')
        self.assertEquals(classify.empty_filter, 3)
        self.assertEquals(classify.filter_by_region['region0'], 0)
        self.assertEquals(classify.filter_by_region['region1'], 1)
        self.assertEquals(classify.filter_by_region['region2'], 2)

    def init_users(self, mock):
        """Method to configure in the mock map the users, projets and roles"""
        count = 10
        users = dict()
        projects = dict()
        roles = dict()
        admin_user = '7'
        for i in range(1, count + 1):
            user = _DictAttr()
            # Admin only has default project id
            if user != admin_user:
                user.cloud_project_id = 'cpi_' + str(i)
            user.default_project_id = 'dpi_' + str(i)
            user.id = str(i)
            users[user.id] = user

        # create projects entries for all tenants but cpi_10 and dpi_10
        for i in range(1, count):
            projects['cpi_' + str(i)] = i
            projects['dpi_' + str(i)] = i

        # create project unrelated with user
        projects['1000'] = 1000

        # create roles for users 1..8 (user9 and user10 will be unknown)
        roles = {
            '1': [BASIC_ROLE_ID], '2': [BASIC_ROLE_ID],
            '3': [COMMUNITY_ROLE_ID], '4': [COMMUNITY_ROLE_ID],
            '5': [TRIAL_ROLE_ID], '6':  [TRIAL_ROLE_ID],
            admin_user: [ADMIN_ROLE_ID], '8': ['OTHER']}

        config = {
            'return_value.users': users,
            'return_value.tenants': projects,
            'return_value.roles_by_user': roles
        }
        mock.configure_mock(**config)

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def test_constructor_process_users(self, mock):
        """Test that the process_users method that is invoked from the
        constructor, fills correctly all the data"""
        self.init_users(mock)
        classify = ClassifyResources('/fakedir')

        self.assertEquals(classify.admin_users, {'7'})
        self.assertEquals(classify.trial_users, {'5', '6'})
        self.assertEquals(classify.community_users, {'3', '4'})
        self.assertEquals(classify.basic_users, {'1', '2'})
        self.assertEquals(classify.other_users, {'8'})
        self.assertEquals(classify.not_found_users, {'9', '10'})

        # Broken users can be of any of the other types (not found, basic...)
        self.assertEquals(classify.broken_users, {'10'})

        self.assertEquals(classify.user_cloud_projects, {
            'cpi_1', 'cpi_2', 'cpi_3', 'cpi_4',
            'cpi_5', 'cpi_6', 'cpi_7', 'cpi_8',
            'cpi_9', 'cpi_10'})

        self.assertEquals(classify.user_default_projects, {
            'dpi_1', 'dpi_2', 'dpi_3', 'dpi_4',
            'dpi_5', 'dpi_6', 'dpi_7', 'dpi_8',
            'dpi_9', 'dpi_10'})

        self.assertEquals(classify.comtrialadmin_cloud_projects, {
            'cpi_3', 'cpi_4', 'cpi_5', 'cpi_6', 'dpi_7'})
        self.assertEquals(classify.basic_cloud_projects, {
            'cpi_1', 'cpi_2'})
        self.assertEquals(classify.community_cloud_projects, {
            'cpi_3', 'cpi_4'})
        self.assertEquals(classify.trial_cloud_projects, {
            'cpi_5', 'cpi_6'})
        self.assertEquals(classify.admin_cloud_projects, {'dpi_7'})
        self.assertEquals(classify.other_users_cloud_projects, {'cpi_8'})
        self.assertEquals(classify.not_found_cloud_projects, {
            'cpi_9', 'cpi_10'})
        self.assertEquals(classify.broken_users_projects, {'cpi_10'})
        self.assertTrue(True)

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def test_print_users_summary(self, mock):
        """This method only prints the results already calculated in
        process users, therefore this method only checks that execution ends
        without errors"""

        self.init_users(mock)
        self.init_filters(mock)
        classify = ClassifyResources('/fakedir', ['region0', 'region1'])
        classify.print_users_summary()

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def test_classify_filter_projects(self, mock):
        """Check the filter_projects methods. The tenant-id that has filters
        and don't include the region, must be discarded. Project without
        filters or with the region's filter, should pass the filter"""
        self.init_users(mock)
        self.init_filters(mock)
        classify = ClassifyResources('/fakedir')
        projects = ['cpi_1', 'cpi_3', 'cpi_7', 'cpi_15']
        filtered = classify.filter_projects(projects, 'region1')
        self.assertItemsEqual(filtered, ['cpi_1', 'cpi_7', 'cpi_15'])

    def init_resources(self, mock):
        """Method to configure in the mock map some resources to test"""

        # Use the same counters for VMs and cinder volumes
        count_resources_by_tenant = {
            'cpi_1': 1, 'cpi_2': 2, 'cpi_3': 4, 'cpi_4': 8, 'cpi_5': 16,
            'cpi_6': 32, 'cpi_7': 64, 'dpi_7': 128, 'cpi_8': 256, 'cpi_9': 512,
            'dpi_1': 1024, 'fake': 2048, '1000': 4096
        }
        self.count_resources_by_tenant = count_resources_by_tenant
        resources_vms = dict()
        resources_volumes = dict()
        for key in count_resources_by_tenant:
            count = count_resources_by_tenant[key]
            while count > 0:
                vm = _DictAttr()
                vm.tenant_id = key
                resources_vms[key + '_' + str(count)] = vm
                volume = _DictAttr()
                volume['os-vol-tenant-attr:tenant_id'] = key
                resources_volumes[key + '_' + str(count)] = volume
                count -= 1

        config = {
            'return_value.vms': resources_vms,
            'return_value.volumes': resources_volumes
        }
        mock.configure_mock(**config)

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def test_classify_resource_raw(self, mock):
        """test classify resource with a known set inserted in the mock"""
        self.init_users(mock)
        self.init_filters(mock)
        self.init_resources(mock)
        classify = ClassifyResources('/fakedir')
        tuple = classify.classify_resource_raw(classify.map.vms, 'region0')
        # Bad region
        self.assertEquals(len(tuple[0]),
                          # community in region1 but not in region0
                          self.count_resources_by_tenant['cpi_4'] +
                          # trial in region1 but not in region0
                          self.count_resources_by_tenant['cpi_5'])
        # Basic + other roles + no role
        self.assertEquals(len(tuple[1]),
                          # basic
                          self.count_resources_by_tenant['cpi_1'] +
                          self.count_resources_by_tenant['cpi_2'] +
                          # other type
                          self.count_resources_by_tenant['cpi_8'] +
                          # unknown type (no role)
                          self.count_resources_by_tenant['cpi_7'] +
                          self.count_resources_by_tenant['cpi_9'])
        # Projects with unknown user
        self.assertEquals(len(tuple[2]),
                          self.count_resources_by_tenant['dpi_1'] +
                          self.count_resources_by_tenant['1000'])

        # Projects with cloudid that does not exists
        self.assertEquals(len(tuple[3]),
                          self.count_resources_by_tenant['fake'])

    @patch('scripts.classify_resources_by_owners.OpenStackMap', auto_spec=True)
    def test_classify_resource(self, mock):
        """check classify resource, that classify_resource_raw is invoked
        with the right parameters; this is tested comparing the result with
        the VM resources, that must return the same numbers"""
        self.init_users(mock)
        self.init_filters(mock)
        self.init_resources(mock)
        classify = ClassifyResources('/fakedir')
        tuple1 = classify.classify_resource_raw(classify.map.vms, 'region0')
        tuple2 = classify.classify_resource('volumes', 'region0')
        for i in range(4):
            self.assertEquals(len(tuple1[i]), len(tuple2[i]))


class TestHiddenSet(unittest.TestCase):
    """Test HiddenSet, a class with hidden set elements where
    the 'in' operator works but are not listed."""
    def test_class(self):
        """Create a class with two elements and add a hidden one
        Verify that the in operator works with the three elements
        and does not work with non-existent elements.

        Also check that the length is 2, that is, the hidden
        element is not counted.
        """
        hset = hidden_set(set(['element1', 'element2']))
        hset.add_hidden('element3_hidden')

        self.assertIn('element1', hset)
        self.assertIn('element2', hset)
        self.assertIn('element3_hidden', hset)
        self.assertNotIn('other_element', hset)
        self.assertEqual(len(hset), 2)
