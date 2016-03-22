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

from subprocess import Popen, PIPE
import json
import os
import os.path
import sys

# default content of the properties file. The passwords are
# also append to this file.

default_values = {
    'KEYSTONE_HOST': '127.0.0.1',
    'REGION': 'RegionOne',
    'CONTROLLER': '127.0.0.1',
    'PUBLIC_CONTROLLER': '127.0.0.1',
    'EXTERNAL_INTERFACE': 'eth2',
    'MANAGEMENT_IPS': '127.0.0',
    'TUNNEL_IPS': '192.168.57',
}


class GenerateTemplateRegion(object):
    """Class to generate the configuration to install openstack and register
    endpoint and users. The class uses a template as input and also generated
    random passwords"""

    # Passwords variables to generate. Keys are generated randomly
    password_parameters = [
        'RABBIT_PASS', 'MYSQL_PASS', 'NOVA_PASS', 'GLANCE_PASS',
        'CINDER_PASS', 'NEUTRON_PASS', 'SWIFT_PASS', 'ADMIN_REGION_PASS',
        'NOVA_DBPASSWORD', 'GLANCE_DBPASSWORD', 'METADATA_SECRET',
        'CINDER_DBPASSWORD', 'NEUTRON_DBPASSWORD', 'SWIFT_DBPASSWORD']

    @staticmethod
    def generate_properties_file(filename='config_vars', env=os.environ):
        """Generate a configuration file, using the template of this module
        and with some random generated password

        :param filename: the output file (default is config_vars)
        :param env: environment to override default values
        :return: nothing
        """

        template = open(os.path.join(os.path.split(sys.argv[0])[0], 'default_region_template')).read()
        p = Popen(["curl", "http://169.254.169.254/latest/meta-data/public-ipv4"], stdout=PIPE)
        publicip, err = p.communicate()
        default_values["PUBLIC_CONTROLLER"] = publicip
        p = Popen(["curl", "http://169.254.169.254/latest/meta-data/Region"], stdout=PIPE)
        publicip, err = p.communicate()
        default_values["PUBLIC_CONTROLLER"] = publicip
        p2 = Popen(["curl", "http://169.254.169.254/openstack/latest/meta_data.json"], stdout=PIPE)
        metadatajson, err = p2.communicate()
        meta = json.loads(metadatajson)["meta"]
        default_values["REGION"] = meta["Region"]
        default_values["KEYSTONE_HOST"] = meta["keystone_ip"]
        values = default_values.copy()
        # override default values with env
        if env:
            for key in values:
                if key in env:
                    values[key] = env[key]
        # replace default values in template
        properties = template.format(**values)

        with open(filename, 'w') as f:
            f.write(properties)
            # generate passwords
            names = GenerateTemplateRegion.password_parameters
            child = Popen(["pwgen", "-s", "-1", "30", str(len(names))], stdout=PIPE)
            child.wait()
            names_iter = iter(names)
            for key in names:
                f.write('export ' + key + '=' + child.stdout.readline())

            # Write credential
            f.write('\n# Admin credential\n')
            f.write('export OS_REGION_NAME=$REGION\n')
            f.write('export OS_AUTH_URL=http://$KEYSTONE_HOST:5000/v3/\n')
            f.write('export OS_AUTH_URL_V2=http://$KEYSTONE_HOST:5000/v2.0/\n')
            f.write('export OS_PASSWORD=$ADMIN_REGION_PASS\n')
            f.write('export OS_USERNAME=admin-$REGION\n')
            f.write('export OS_TENANT_NAME=$OS_USERNAME\n')
            f.write('export OS_PROJECT_DOMAIN_ID=default\n')
            f.write('export OS_USER_DOMAIN_NAME=Default\n')
            f.write('export OS_IDENTITY_API_VERSION=3\n')


if __name__ == '__main__':
    GenerateTemplateRegion.generate_properties_file()
