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

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as et
import logging
import warnings


class BluePrintResources(object):
    """This class represent the BluePrint resources of a tenant. It includes
    methods to list and delete the templates"""
    def __init__(self, osclients):
        """Constructor. It requires an OpenStackClients object

        :param openstackclients: an OpenStackClients method (module osclients)
        :return: nothing
        """
        self.osclients = osclients
        self.tenant_id = osclients.get_tenant_id()
        self.url_base = osclients.get_public_endpoint('paas', osclients.region)
        self.url_temp = self.url_base + '/catalog/org/FIWARE/vdc/' + \
            self.tenant_id + '/environment'
        self.url_blue = self.url_base + '/envInst/org/FIWARE/vdc/' + \
            self.tenant_id + '/environmentInstance'

        self.headers = {'X-Auth-Token': self.osclients.get_token(),
                        'Tenant-id': self.tenant_id,
                        'Content-type': 'application/xml'}
        warnings.simplefilter('ignore', category=InsecureRequestWarning)

    def get_tenant_blueprints(self):
        """Return a list with all the blueprint instances of the tenant.
        :return: a list of blueprint instance names. None if error
        """
        err_msg = 'Obtaining blueprint instances from tenant {0} failed. '\
                  'Reason: {1}'
        try:
            response = requests.get(self.url_blue, headers=self.headers,
                                    verify=False)
        except Exception, e:
            logging.error(err_msg.format(self.tenant_id, str(e)))
            return None
        if response.status_code != 200:
            logging.error(err_msg.format(self.tenant_id),
                          str(response.status_code) + ' ' + response.reason)
            return None
        tree = et.fromstring(response.content)
        return list(name.text for name in tree.findall(
            './environmentInstancePDto/blueprintName'))

    def delete_tenant_blueprint(self, blueinstance_id):
        """Delete the specified blueprint instance.
        :param blueinstance_id: the id of the blueprint
        :return: True if success
        """
        err_msg = 'Deleting blueprint instance {1} from tenant {0} failed. '\
                  'Reason: {2}'
        try:
            response = requests.delete(self.url_blue + '/' + blueinstance_id,
                                       headers=self.headers, verify=False)
        except Exception, e:
            msg = err_msg.format(self.tenant_id, blueinstance_id, str(e))
            logging.error(msg)
            return False

        if response.status_code not in (200, 204):
            msg = err_msg.format(self.tenant_id, blueinstance_id,
                                 str(response.status_code) + ' ' +
                                 response.reason)
            logging.error(msg)
            return False
        else:
            return True

    def delete_tenant_blueprints(self):
        """Delete all the blueprint instances of the tenant
        :return: True if success
        """
        err_msg = 'Deleting blueprint instances from tenant {0} failed.'
        blueprints = self.get_tenant_blueprints()
        if blueprints is None:
            logging.error(err_msg.format(self.tenant_id))
            return False

        failed = False
        for blueprint_instance in blueprints:
            if not self.delete_tenant_blueprint(blueprint_instance):
                failed = True
        return not failed

    def get_tenant_templates(self):
        """Return a list with all the templates of the tenant. Templates are
        identified by its name
        :return: a list of template ids, None if error"""
        err_msg = 'Obtaining blueprint templates from tenant {0} failed. '\
                  'Reason: {1}'
        try:
            response = requests.get(self.url_temp, headers=self.headers,
                                    verify=False)
        except Exception, e:
            logging.error(err_msg.format(self.tenant_id, str(e)))
            return None
        if response.status_code != 200:
            logging.error(err_msg.format(self.tenant_id),
                          str(response.status_code) + ' ' + response.reason)
            return None
        tree = et.fromstring(response.content)
        return list(nam.text for nam in tree.findall('./environmentDto/name'))

    def delete_tenant_template(self, environment_id):
        """Delete the specified template.
        :param environment_id: the id of the template
        :return: True if success
        """
        err_msg = 'Deleting blueprint template {1} from tenant {0} failed. '\
                  'Reason: {2}'
        try:
            response = requests.delete(self.url_temp + '/' + environment_id,
                                       headers=self.headers, verify=False)
        except Exception, e:
            msg = err_msg.format(self.tenant_id, environment_id, str(e))
            logging.error(msg)
            return False

        if response.status_code not in (200, 204):
            msg = err_msg.format(self.tenant_id, environment_id,
                                 str(response.status_code) + ' ' +
                                 response.reason)
            logging.error(msg)
            return False
        else:
            return True

    def delete_tenant_templates(self):
        """Delete all the templates from the tenant.
        :return: True if success
        """
        err_msg = 'Deleting blueprint templates from tenant {0} failed.'
        templates = self.get_tenant_templates()
        if templates is None:
            logging.error(err_msg.format(self.tenant_id))
            return False

        failed = False

        for template in templates:
            if not self.delete_tenant_template(template):
                failed = True
        return not failed
