#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Telefónica Investigación y Desarrollo, S.A.U
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
#

import json
import re
import os
import sys
from fiwareskuld.change_password import PasswordChanger

from keystoneclient.exceptions import NotFound

from fiwareskuld.utils.osclients import OpenStackClients


# default JSON template. Variables are expanded with environment
default_region_json = """
{
    "region": "$REGION",
    "update_passwords": false,
    "users": [
        {
            "username": "glance",
            "password": "$GLANCE_PASS"
        },
        {
            "username": "nova",
            "password": "$NOVA_PASS"
        },
        {
            "username": "cinder",
            "password": "$CINDER_PASS"
        },
        {
            "username": "neutron",
            "password": "$NEUTRON_PASS"
        },
        {"username": "swift", "password": "$SWIFT_PASS"},
        {"username": "admin-$REGION", "password": "$ADMIN_REGION_PASS"}
    ],
    "services": [
        {
            "name": "glance",
            "type": "image",
            "public": "http://$PUBLIC_CONTROLLER:9292",
            "admin": "http://$CONTROLLER:9292",
            "internal": "http://$CONTROLLER:9292"
        },
        {
            "name": "nova",
            "type": "compute",
            "public": "http://$PUBLIC_CONTROLLER:8774/v2/%(tenant_id)s",
            "admin": "http://$CONTROLLER:8774/v2/%(tenant_id)s",
            "internal": "http://$CONTROLLER:8774/v2/%(tenant_id)s"
        },
        {
            "name": "cinder",
            "type": "volume",
            "public": "http://$PUBLIC_CONTROLLER:8776/v1/%(tenant_id)s",
            "admin": "http://$CONTROLLER:8776/v1/%(tenant_id)s",
            "internal": "http://$CONTROLLER:8776/v1/%(tenant_id)s"
        },
        {
            "name": "cinderv2",
            "type": "volumev2",
            "public": "http://$PUBLIC_CONTROLLER:8776/v2/%(tenant_id)s",
            "admin": "http://$CONTROLLER:8776/v2/%(tenant_id)s",
            "internal": "http://$CONTROLLER:8776/v2/%(tenant_id)s"
        },
        {
            "name": "neutron",
            "type": "network",
            "public": "http://$PUBLIC_CONTROLLER:9696",
            "admin": "http://$CONTROLLER:9696",
            "internal": "http://$CONTROLLER:9696"
        },
        {
            "name": "neutron",
            "type": "network",
            "public": "http://$PUBLIC_CONTROLLER:9696",
            "admin": "http://$CONTROLLER:9696",
            "internal": "http://$CONTROLLER:9696"
        },
        {
            "name": "swift",
            "type": "object-store",
            "public": "http://$PUBLIC_CONTROLLER:8080/v1/AUTH_%(tenant_id)s",
            "admin": "http://$CONTROLLER:8080/v1/AUTH_%(tenant_id)s",
            "internal": "http://$CONTROLLER:8080/v1/AUTH_%(tenant_id)s"
        },
        {
            "name": "keystone",
            "type": "identity",
            "public": "http://$KEYSTONE_HOST:35357/v3/",
            "admin": "http://$KEYSTONE_HOST:5000/v3/",
            "internal": "http://$KEYSTONE_HOST:35357/v3/"
        }
    ]
}
"""


class RegisterRegion(object):
    """Class to register users with role assignments, services and endpoints"""
    def __init__(self):
        """constructor"""
        self.osclients = OpenStackClients()
        self.keystone = self.osclients.get_keystoneclient()
        self.password_changer = PasswordChanger(self.osclients)

    def service_exists(self, service_name, service_type):
        """Ensure that the service exists: create if it does not.

        :param service_name: the service name (e.g. nova)
        :param service_type: the service type (e.g. compute)
        :return: the service id
        """
        try:
            service = self.keystone.services.find(name=service_name)
        except NotFound:
            service = self.keystone.services.create(name=service_name, type=service_type)
        return service.id

    def region_exists(self, region_id):
        """ Ensure that the region exists: create if it does not.

        :param region_id: the region id (the region name)
        :return: Nothing
        """
        if not self.is_region(region_id):
            self.keystone.regions.create(region_id)

    def is_region(self, region_id):
        """
        It checks if the region exists.
        :param region_id: the region id
        :return: True/False
        """
        regions = self.keystone.regions.list()
        for region in regions:
            if region.id == region_id:
                return True
        return False

    def project_exists(self, tenant_name, domain_id='default'):
        """Ensure that the project exists: create if it does not.

        :param tenant_name: the tenant (aka project)
        :param domain_id: the domain-id (or default)
        :return: the project (a.k.a. tenant) id
        """
        try:
            project = self.keystone.projects.find(name=tenant_name)
        except NotFound:
            project = self.keystone.projects.create(tenant_name, domain_id)
        return project.id

    def user_exists(self, username, password, set_passwords=False):
        """check that user exists, create him/her otherwise. If the user
        exists and set_password is True, it sets the password.

        :param username: the username of the user
        :param password: the password of the user
        :param set_passwords: if True and the user exists, change the password
        :return: the user object
        """
        try:
            user = self.keystone.users.find(name=username)
            if set_passwords:
                self.password_changer.change_password(user, password)
        except NotFound:
            user = self.keystone.users.create(name=username, password=password)
        return user

    def delete_spain2_regions(self):
        service_id = self.keystone.services.find(name="keystone")
        try:
            end1 = self.keystone.endpoints.find(service=service_id, interface='public', region='Spain2')
            self.keystone.endpoints.delete(end1)
        except:
            pass
        try:
            end2 = self.keystone.endpoints.find(service=service_id, interface='admin', region='Spain2')
            self.keystone.endpoints.delete(end2)
        except:
            pass
        try:
            end3 = self.keystone.endpoints.find(service=service_id, interface='internal', region='Spain2')
            self.keystone.endpoints.delete(end3)
        except:
            pass

    def endpoint_exists(self, service_id, interface, url, region):
        """check that enpoint exists. Otherwise, create it. Also check that the
        URLs are the same; if they are different, update.

        :param service_id: the service id
        :param interface: interface may be public, internal, admin.
        :param url: the URL of the endpoint
        :param region: the region id.
        :return: the endpoint id.
        """
        endpoint = self.get_endpoint(service_id, interface, region)
        if endpoint:
            result = endpoint
            if result.url != url:
                self.keystone.endpoints.update(result.id, url=url)

        else:
            result = self.keystone.endpoints.create(service=service_id, interface=interface,
                                                    url=url, region=region)

        return result.id

    def get_endpoint(self, service_id, interface, region_id):
        """
        It obtains the endpoint
        :param service_id: the service associated
        :param interface: the interface
        :param region_id: the region
        :return: the endpoint
        """
        endpoints = self.keystone.endpoints.list(service=service_id, interface=interface)

        for endpoint in endpoints:
            if endpoint.region == region_id:
                return endpoint
        return None

    def register_region(self, region, set_passwords=False):
        """Register the region data. It is intended to create all the users
        and services required to add a region to a federation.

        This method is idempotent, that is, the effect of invoking it multiple
        times is the same that invoking only once.

        It ensure that the region region['region'] is registered.
        It ensure that the users region['users'] exist and have
         the role admin in the service project
        It ensure that the services region['services'] and its endpoints
        exist and the URLs are correct.

        :param region: a dictionary extracted from a JSON with the structure of
        default_region_json

        :param set_passwords: if true, override the passwords when the user
         exists. If false, passwords are only used when the users are created.
        :return: nothing
        """
        region_name = region['region']
        self.region_exists(region_name)

        for user in region['users']:
            userobj = self.user_exists(user['username'], user['password'])
            admin_role = self.keystone.roles.find(name='admin')
            if user['username'].startswith('admin-'):
                # admin users use their own tenant instead of the service one
                project = self.project_exists(user['username'])
            else:
                project = self.project_exists('service')

            self.keystone.roles.grant(admin_role, user=userobj, project=project)

        for s in region['services']:
            service_id = self.service_exists(s['name'], s['type'])
            self.endpoint_exists(service_id, 'public', s['public'], region_name)
            self.endpoint_exists(service_id, 'admin', s['admin'], region_name)
            self.endpoint_exists(service_id, 'internal', s['internal'], region_name)

    @staticmethod
    def transform_json(data, env):
        """Utility method, to expand ${VAR} and $VAR in data, using env
        variables

        :param data: the template to process
        :param env: array with the variables
        :return: the template with the variables expanded
        """
        var_shell_pattern_c = re.compile(r'\${{(\w+)}}')
        var_shell_pattern = re.compile(r'\$(\w+)')
        data = data.replace('{', '{{')
        data = data.replace('}', '}}')
        data = var_shell_pattern_c.sub(r'{\1}', data)
        data = var_shell_pattern.sub(r'{\1}', data)
        return data.format(**env)

    def register_regions(self, regions_json=default_region_json, env=os.environ):
        """This is a front-end of the method register region, that receives
        as parameter the JSON and the environment to override the ${VAR} and
        $VAR expressions.

        It admits a JSON with an only region (with the structure of
        default_region_json) or a JSON with multiple regions. This last has
        a 'regions' fields that is an array of regions.

        :param regions_json: a JSON
        :param env: an environment (array of variables)
        :return: nothing
        """
        regions_json = self.transform_json(regions_json, env)
        region = json.loads(regions_json)
        if 'SET_OPENSTACK_PASSWORDS' in env:
            set_passwords = True
        else:
            set_passwords = False
        if 'regions' in region:
            # This is an array of regions
            for r in region:
                self.register_region(r, set_passwords)
        else:
            # This is an only region
            self.register_region(region, set_passwords)

# If the program receives a parameter, it is interpreted as a file with the
# JSON to register. Otherwise, it uses default_region_json, replacing the
# variables with the environment.

if __name__ == '__main__':
    register = RegisterRegion()
    register.delete_spain2_regions()
    if len(sys.argv) == 2:
        json_data = open(sys.argv[1]).read()
        register.register_regions(json_data)
    else:
        register.register_regions()
