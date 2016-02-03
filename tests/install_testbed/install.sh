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

add_iface() {
ip a show dev $1 |grep "inet " || cat <<EOF | sudo tee /etc/network/interfaces.d/$1.cfg >/dev/null
auto $1
iface $1 inet dhcp
EOF
sudo ifup $1
}

# add alias to use nova with keystone URL v2
echo alias nova=\'env OS_AUTH_URL=\$OS_AUTH_URL_V2 nova\' > ~/.bash_aliases

# add hostname to /etc/hosts to avoid warning with sudo. This could
# affect the parsing of some commands.
echo "127.0.0.1 localhost $(hostname)" > /tmp/host.new
tail -n +2 /etc/hosts >> /tmp/host.new

# Add network configuration for eth1 and eth2. These is needed because
# we are using an installation with an only node.
# eth1: tunnel
add_iface eth1
# eth2: external network
add_iface eth2

# Copy, instead of moving to use security context of the directory.
cat /tmp/host.new | sudo tee /etc/hosts >/dev/null
rm /tmp/host.new

# download fiware-skuld project
cd
git clone https://github.com/telefonicaid/fiware-skuld.git
# Remove these two lines before merge
cd ~/fiware-skuld
git checkout feature_CLAUDIA-5785


cd ~/fiware-skuld/tests/install_testbed

# create properties file, register region
./keystone_work.sh


# install controller (this might be run in another node)
sudo ./prepare_controller.sh
sudo ./install_glance.sh
sudo ./install_nova_controller.sh
sudo ./install_neutron_controller.sh

# install node (this might be run in other nodes)
sudo ./prepare_node.sh
sudo ./install_nova_node.sh
sudo ./install_neutron_node.sh
sudo ./install_neutron_compute_node.sh

# Create image, networs and VM
./create_resources.sh

