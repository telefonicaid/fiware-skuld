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
from mock import MagicMock, patch
import os
import time
from oslo_utils import timeutils


from fiwareskuld.impersonate import TrustFactory, TRUSTID_VALIDITY

__author__ = 'chema'


class TestTrustFactoryConstructor(unittest.TestCase):
    """class to test constructor of TrustFactory"""
    def setUp(self):
        """delete KEYSTONE_ADMIN_ENDPOINT"""
        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            self.saved_keystone_admin = os.environ['KEYSTONE_ADMIN_ENDPOINT']
            del os.environ['KEYSTONE_ADMIN_ENDPOINT']
        else:
            self.saved_keystone_admin = None

    def tearDown(self):
        """restore KEYSTONE_ADMIN_ENDPOINT"""
        if self.saved_keystone_admin:
            os.environ['KEYSTONE_ADMIN_ENDPOINT'] = self.saved_keystone_admin
        else:
            if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
                del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    def assertCommonCalls(self, mock, object):
        """commons calls in all the versions of the constructor"""
        self.assertTrue(mock.called)
        self.assertTrue(mock.return_value.get_keystoneclientv3.called)
        self.assertEquals(object.keystone, mock().get_keystoneclientv3())

    @patch('fiwareskuld.impersonate.osclients.OpenStackClients', auto_spec=True)
    def test_constructor_no_params(self, mock):
        """test call to constructor without params nor environment"""
        trustfactory = TrustFactory()
        self.assertFalse(mock.return_value.override_endpoint.called)
        self.assertEquals(trustfactory.trustid_validity, TRUSTID_VALIDITY)
        self.assertCommonCalls(mock, trustfactory)

    @patch('fiwareskuld.impersonate.osclients.OpenStackClients', auto_spec=True)
    def test_constructor_no_params_with_environ(self, mock):
        """test constructo without params but with KEYSTONE_ADMIN_ENDPOINT"""
        os.environ['KEYSTONE_ADMIN_ENDPOINT'] = 'foo'
        trustfactory = TrustFactory()
        self.assertTrue(mock.return_value.override_endpoint.called)
        self.assertCommonCalls(mock, trustfactory)

    @patch('fiwareskuld.impersonate.osclients.OpenStackClients', auto_spec=True)
    def test_constructor_params_validity(self, mock):
        """test constructor passing trustid_validity"""
        trustfactory = TrustFactory(trustid_validity=0)
        self.assertEquals(trustfactory.trustid_validity, 0)
        self.assertCommonCalls(mock, trustfactory)

    def test_constructor_params_moks(self):
        """test constructor passing an instance of osclients
        (a mock is used)"""
        mock = MagicMock()

        trustfactory = TrustFactory(mock)
        self.assertTrue(mock.get_keystoneclientv3.called)
        self.assertEquals(trustfactory.keystone, mock.get_keystoneclientv3())


class TestTrustFactory(unittest.TestCase):
    """class to test methods of TrustFactory"""
    def setUp(self):
        """create object and init object.keystone with a mock"""
        self.trustfactory = TrustFactory(MagicMock())
        self.trustfactory.keystone = MagicMock()

    def assertCreateResult(self, result, trustor):
        """check the result tuple"""
        self.assertEquals(result[0], trustor.name)
        self.assertEquals(result[1], 'generatedtrustid')
        self.assertEquals(result[2], trustor.id)

    def test_create_trust(self):
        """check result of create_trust"""
        trustor = MagicMock(id='trustor_id', name='trustor_name')
        trust = MagicMock(id='generatedtrustid')
        config = {'users.get.return_value': trustor,
                  'trusts.create.return_value': trust}
        self.trustfactory.keystone.configure_mock(**config)
        result = self.trustfactory.create_trust('trustor_id', 'trustee_id')
        self.assertCreateResult(result, trustor)

    def test_create_trust_admin(self):
        """check externals calls and result of create_trust_admin"""
        resp = MagicMock()
        body_response = {'trust': {'id': 'generatedtrustid'}}
        trustor = MagicMock(id='trustor_id', name='trustor_name',
                            cloud_project_id='trustor_tenant')
        trustee = MagicMock(id='trustee_id', name='trustee_name')
        config = {
            'trusts.client.post.return_value': (resp, body_response),
            'users.get.return_value': trustor,
            'users.find.return_value': trustee
        }
        self.trustfactory.keystone.configure_mock(**config)

        now = time.time()
        with patch('fiwareskuld.impersonate.time.time') as time_mock:
            time_mock.configure_mock(return_value=now)
            result = self.trustfactory.create_trust_admin(
                'trustor_id', 'trustee_name')

            # check result
            self.assertCreateResult(result, trustor)

        # check call
        body = {'trust': {'impersonation': True, 'trustor_user_id': trustor.id,
                          'allow_redelegation': True,
                          'roles': [{'name': 'owner'}],
                          'expires_at': timeutils.iso8601_from_timestamp(
                              now + self.trustfactory.trustid_validity, True),
                          'trustee_user_id': trustee.id,
                          'project_id': trustor.cloud_project_id}}
        self.trustfactory.keystone.trusts.client.post.assert_called_once_with(
            'OS-TRUST/trusts_for_admin', body=body)

    def test_delete_trust(self):
        """test delete_trust method call to keystone client"""
        id = 'id1'
        self.trustfactory.delete_trust(id)
        self.trustfactory.keystone.trusts.delete.assert_called_once_with(id)

    def test_delete_trust_admin(self):
        """test delete_trust_admin method call to keystone client"""
        id = 'id1'
        resp = MagicMock()
        config = {'users.client.delete.return_value': (resp, 'body')}
        self.trustfactory.keystone.configure_mock(**config)

        return_value = self.trustfactory.delete_trust_admin(id)
        self.trustfactory.keystone.users.client.delete.assert_called_once_with(
            'OS-TRUST/trusts_for_admin/' + id)
        self.assertEquals(return_value, resp.ok)
