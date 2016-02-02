#!/bin/bash -ex
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
#
# Author: Chema

. config_vars

neutron net-create ext-net --router:external True --provider:physical_network external --provider:network_type flat
neutron subnet-create ext-net --name ext-subnet --allocation-pool start=${NEUTRON_IPS}.2,end=${NEUTRON_IPS}.254  --disable-dhcp --gateway ${NEUTRON_IPS}.1 ${NEUTRON_IPS}.0/24
neutron net-create shared-net
neutron subnet-create shared-net --name shared-subnet --gateway 192.168.2.1 192.168.2.0/24
neutron router-create shared-router
neutron router-interface-add shared-router shared-subnet
neutron router-gateway-set shared-router ext-net

wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
glance image-create --name cirros --container bare --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --is-public True
NETID=$(neutron net-list |awk '/shared-net/ { print $2 }')
env OS_AUTH_URL=http://$KEYSTONE_HOST:5000/v2.0/ nova boot testvm --flavor m1.tiny --image cirros --nic net-id=$NETID