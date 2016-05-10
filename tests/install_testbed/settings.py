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
__author__ = 'chema'

key_name = 'testbedskuld_key'
security_group = 'testbedskuld_sg'
# Use this IP if it is available.
preferred_ip = None

# Testbed image
flavor_name = 'm1.large'
flavor_name_phone_home = "m1.small"
image_name = 'keyrock-R4.4'
image_phone_home = 'base_ubuntu_14.04'
vm_name = 'testbedskuld'
# filename of init_script
init_script = 'cloudconfig'
init_script_only_glance = 'cloudconfig_only_glance'
init_script_phone_home = 'cloudconfig_phone_home'

# Accept ICMP and SSH (TCP 22) traffic from these ranges of IPs
# 0.0.0.0/0 means any IP
ingress_icmp_ip_range = '0.0.0.0/0'
ingress_ssh_ip_range = '0.0.0.0/0'

# multinetwork uses two extra networks: tunnel and external. However this
# configuration is not working at the moment and the supported option is
# multinetwork = False, that uses TAP interfaces that only work inside the
# VM so simulate the tunnel and external networks.
multinetwork = False

network_names = {'management': 'node-int-net-01'}
subnet = {}


if multinetwork:
    network_names['tunnel'] = 'tunnel-net'
    network_names['external'] = 'external-net'

    subnet['tunnel'] = '192.168.57.0/24'
    subnet['external'] = '192.168.58.0/24'

    # Test image. Only used when multinetwork == True
    flavor_name_test = 'm1.tiny'
    image_name_test = 'base_debian_7'
    vm_name_test = 'testvm'
