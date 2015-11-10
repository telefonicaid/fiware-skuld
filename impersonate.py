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
import os
from oslo_utils import timeutils
import time

import osclients
try:
    from settings.settings import TRUSTID_VALIDITY
except ImportError:
    TRUSTID_VALIDITY = 36000


class TrustFactory:
    """This class is used to create/destroy a TRUST_ID, that allows a user (the
     trustee) to impersonate another user (the trustor).

    The mainstream functionalily only allows to the trustor create the TRUST_ID
    but this class uses a change in the FiWare IDM that allows admin user
    to create any TRUST_ID"""

    def __init__(self, osclients_o=None, trustid_validity=TRUSTID_VALIDITY):
        """
        Constructor
        :param osclients_o: a osclients object; by default this object
        is built using the environment variables (OS_AUTH_URL, OS_PASSWORD...)
        :param trustid_validity: number of seconds the TRUST_ID last. It can
        be also released manually.
        """
        if not osclients_o:
            osclients_o = osclients.OpenStackClients()

        if 'KEYSTONE_ADMIN_ENDPOINT' in os.environ:
            osclients_o.override_endpoint(
                'identity', osclients_o.region, 'admin',
                os.environ['KEYSTONE_ADMIN_ENDPOINT'])

        self.keystone = osclients_o.get_keystoneclientv3()
        self.trustid_validity = trustid_validity

    def create_trust_admin(self, trustor_id, trustee_name):
        """
        Create a TRUST_ID. This method must be invoked by the administrator and
        only works if the keystone server has been adapted to allow the
        administrator to create a TRUST_ID for other users.

        :param trustor_id the user id of the trustor user (who is
        impersonated by the trustee)
        :param trustee_name: the user name of the trustee user (who
        impersonates the trustor)
        :return: the tuple (trustor_username, trust_id, trustor_id), None
                 if error
        """
        trustor = self.keystone.users.get(trustor_id)
        trustee = self.keystone.users.find(name=trustee_name)
        data = dict()
        data['impersonation'] = True
        data['allow_redelegation'] = True
        data['project_id'] = trustor.cloud_project_id
        data['roles'] = [{'name': 'owner'}]
        data['trustee_user_id'] = trustee.id
        data['trustor_user_id'] = trustor.id
        data['expires_at'] = timeutils.iso8601_from_timestamp(
            time.time() + self.trustid_validity, True)
        # data['remaining_uses'] = 1
        request = {'trust': data}
        (resp, body_resp) = self.keystone.trusts.client.post(
            'OS-TRUST/trusts_for_admin', body=request)
        if resp.ok:
            return trustor.name, body_resp['trust']['id'], trustor.id
        else:
            return None

    def create_trust(self, trustor_id, trustee_id):
        """
        Create a TRUST_ID. This method must be invoked by trustor, that is, the
        user to be impersonated by the trustee.

        :param trustor_id the user id of the trustor user (who is
        impersonated by the trustee)
        :param trustee_id: the user id of the trustee user (who
        impersonates the trustor)
        :return: the tuple (trustor_username, trust_id, trustor_id), None if
                 error
        """

        trustor = self.keystone.users.get(trustor_id)
        expire = timeutils.datetime.datetime.fromtimestamp(
            time.time() + self.trustid_validity)
        trust = self.keystone.trusts.create(
            trustee_id, trustor_id, ['owner'], trustor.cloud_project_id,
            True, expire)
        if trust:
            return trustor.name, trust.id, trustor.id
        else:
            return None

    def delete_trust(self, trust_id):
        """Delete and invalidate a trust_id. This method must be called for
        the trustor o more frequently, by the trustee after the
        work required by the token is finished.

        :param trust_id: the trust_id to delete
        :return: True if success
        """
        return self.keystone.trusts.delete(trust_id)

    def delete_trust_admin(self, trust_id):
        """Delete and invalidate a TRUST_ID

        WARNING: This method currently does not work.  It requires changes in
        the keystone server. Use delete_trust with the trustee identity instead.
        :param trust_id:
        :return: True if success
        """
        (resp, body) = self.keystone.users.client.delete(
            'OS-TRUST/trusts_for_admin/' + trust_id)
        return resp.ok
