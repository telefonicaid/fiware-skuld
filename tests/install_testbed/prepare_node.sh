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

add_tap_ifaces() {
cat <<EOF |sudo tee /etc/network/interfaces.d/eth1.cfg >/dev/null
auto eth1
iface eth1 inet static
address 192.168.57.1
netmask 255.255.255.0
pre-up ip tuntap add mode tap eth1
post-down ip tuntap del mode tap eth1
EOF
sudo ifup eth1
cat <<EOF |sudo tee /etc/network/interfaces.d/eth2.cfg >/dev/null
auto eth2
iface eth2 inet manual
pre-up ip tuntap add mode tap eth2
post-down ip tuntap del mode tap eth2
up ip link set dev eth2 up
down ip link set dev eth2 down
EOF
sudo ifup eth2
}

add_iface() {
cat <<EOF > /etc/network/interfaces.d/$1.cfg
auto $1
iface $1 inet dhcp
EOF
sudo ifup $1
}

# check network interfaces
if [ "$(ip link show eth1 2>/dev/null)" ] ; then
   # configure eth1 to use dhcp if it is not already configured,
   # let eth2 unconfigured (it is used in a bridge)
   ip a show dev eth1 |grep "inet " || add_iface eth1
else
   # there are not eth1/eth2. Create them using TAP devices
   add_tap_ifaces
fi

export DEBIAN_FRONTEND=noninteractive

if [ ! -f /etc/apt/sources.list.d/cloudarchive-juno.list ]
then
  apt-get install ubuntu-cloud-keyring
  echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu" \
    "trusty-updates/juno main" > /etc/apt/sources.list.d/cloudarchive-juno.list

  apt-get update && apt-get -y dist-upgrade
fi

# nova boot finish with error when nova compute has /etc/machine-id and it is
# empty.
if [ -f /etc/machine-id ] ; then
   size=$(stat -c "%s" /etc/machine-id)
   if [ $size -eq 0 ] ; then
      rm /etc/machine-id
   fi
fi
