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

# if interface does not have IP, assign it. It only works with
# netmask 255.255.255.0 addresses, using the .1 IP.

if [ ! "$(ip a show dev $EXTERNAL_INTERFACE |grep 'inet ')" ]
then
cat <<EOF > /etc/network/interfaces.d/eth1.cfg
auto $EXTERNAL_INTERFACE
iface eth1 inet static
   address ${NEUTRON_IPS}.1
   netmask 255.255.255.0
EOF
sudo ifup eth1
fi

#ip tuntap add mode tap extdev0
#ip address add dev extdev0 $IP_EXTDEV0
