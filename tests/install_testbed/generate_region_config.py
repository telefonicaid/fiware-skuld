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
__author__ = 'chema'

from subprocess import Popen, PIPE
import os

# default content of the properties file. The passwords are
# also append to this file.

default_values = {
    'KEYSTONE_HOST': '127.0.0.1',
    'REGION': 'Spain2',
    'CONTROLLER': '127.0.0.1',
    'VM_ACCESS_IP': '$CONTROLLER',
    'EXTERNAL_INTERFACE': 'eth1',
    'NOVA_IPS': '192.168.56',
    'NEUTRON_IPS': '192.168.57',
}

template = """
# Provided parameters. Do not change this.

export KEYSTONE_HOST="{KEYSTONE_HOST}"
export AUTH_URI="http://$KEYSTONE_HOST:5000/v2.0"
export IDENTITY_URI="http://$KEYSTONE_HOST:35357"

# Required parameters. If changed, they
# must be provided to register the new
# values.
export REGION="{REGION}"
export CONTROLLER="{CONTROLLER}"

# Set the IP used to connect to remotely control the VM. If undefined, it is
# used the IP visible on Internet, asking to http://ifconfig.me/ip.
# When using nova, usually this is the floating IP, but
# not all nova installations use public IPs and a transparent proxy also might
# affect the result.
export VM_ACCESS_IP={VM_ACCESS_IP}

# Database. These are only default values,
# they may be changed at your convenience.
export GLANCE_DB="glance"
export NOVA_DB="nova"
export NEUTRON_DB="neutron"
export GLANCE_DBUSER="$GLANCE_DB"
export NOVA_DBUSER="$NOVA_DB"
export NEUTRON_DBUSER="$NEUTRON_DB"

# Other defaults
export EXTERNAL_INTERFACE='{EXTERNAL_INTERFACE}'
export NOVA_IPS='{NOVA_IPS}'
export NEUTRON_IPS='{NEUTRON_IPS}'

# Passwords are generated automatically.
# Most of them can be changed by any other value. However, the following
# passwords are associated with keystone accounts and cannot be modified without
# changing them also in keystone:
# NOVA_PASS, GLANCE_PASS, CINDER_PASS, SWIFT_PASS, NEUTRON_PASS, ADMIN_REGION_PASS
"""

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
            f.write('export OS_PASSWORD=$ADMIN_REGION_PASS\n')
            f.write('export OS_USERNAME=admin-$REGION\n')
            f.write('export OS_TENANT_NAME=$OS_USERNAME\n')
            f.write('export OS_PROJECT_DOMAIN_ID=default\n')
            f.write('export OS_USER_DOMAIN_NAME=Default\n')
            f.write('export OS_IDENTITY_API_VERSION=3\n')


if __name__ == '__main__':
    GenerateTemplateRegion.generate_properties_file()