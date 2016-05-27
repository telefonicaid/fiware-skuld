#!/bin/bash -ex
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
# Author: Chema

. config_vars

neutron net-create ext-net --router:external True --provider:physical_network external --provider:network_type flat
neutron subnet-create ext-net --name ext-subnet --allocation-pool start=192.168.58.200,end=192.168.58.219  --disable-dhcp --gateway 192.168.58.1 192.168.58.0/24
neutron net-create shared-net --shared
neutron subnet-create shared-net --name shared-subnet --gateway 192.168.59.1 192.168.59.0/24
neutron router-create shared-router
neutron router-interface-add shared-router shared-subnet
neutron router-gateway-set shared-router ext-net

wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
glance image-create --name cirros --container bare --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --is-public True
NETID=$(neutron net-list |awk '/shared-net/ { print $2 }')
export OS_AUTH_URL=$OS_AUTH_URL_V2

# create a keypair and copy the private key in ~/.ssh with the right
# permission.
nova keypair-add testkey > ~/.ssh/testkey ; chmod 700 ~/.ssh/testkey
# create security group that opens port 22 (SSH) and ICMP (e.g. ping) to
# INGRESS traffic from any IP (0.0.0.0/0)
nova secgroup-create ssh "open tcp 22 and icmp"
nova secgroup-add-rule ssh tcp 22 22 0.0.0.0/0
nova secgroup-add-rule ssh icmp -1 -1 0.0.0.0/0

# 64MB RAM 1 GB disk, 1 VCPU
nova flavor-create micro auto 64 1 1
# 64MB RAM 0 GB disk, 1 VCPU
nova flavor-create micro2 auto 64 0 1

# boot the VM
nova boot testvm --poll --flavor micro2 --image cirros --nic net-id=$NETID --key-name testkey --security-groups ssh

# add a floating IP
. ~/skuldenv/bin/activate
TEST_VM="o.nova.servers.find(name='testvm')"
FLOATING_IP="o.nova.floating_ips.create('ext-net').ip"
~/fiware-skuld/fiwareskuld/utils/osclients.py "${TEST_VM}.add_floating_ip(${FLOATING_IP})"
cp config_vars ~
