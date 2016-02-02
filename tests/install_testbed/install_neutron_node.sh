#!/bin/bash -x
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
# Authors: Jose Ignacio Carretero Guarde and Chema

. ./config_vars

INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS=`ip a| awk "/inet $TUNNEL_IPS/  {print gensub(/\/../,\"\",\"g\",\\$2)}"`


### configure rp_filter and ipforwarding.
grep ^net.ipv4.ip_forward /etc/sysctl.conf
res=$?
[ $res -eq 0 ] && sed -i 's|^net.ipv4.ip_forward.*|net.ipv4.ip_forward=1|g' /etc/sysctl.conf
[ $res -eq 1 ] && echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

grep ^net.ipv4.conf.all.rp_filter /etc/sysctl.conf
res=$?
[ $res -eq 0 ] && sed -i 's|^net.ipv4.conf.all.rp_filter.*|net.ipv4.conf.all.rp_filter=0|g' /etc/sysctl.conf
[ $res -eq 1 ] && echo "net.ipv4.conf.all.rp_filter=0" >> /etc/sysctl.conf

grep ^net.ipv4.conf.default.rp_filter /etc/sysctl.conf
res=$?
[ $res -eq 0 ] && sed -i 's|^net.ipv4.conf.default.rp_filter.*|net.ipv4.conf.default.rp_filter=0|g' /etc/sysctl.conf
[ $res -eq 1 ] && echo "net.ipv4.conf.default.rp_filter=0" >> /etc/sysctl.conf

sysctl -p

set -e
### Install packages
apt-get install -y neutron-plugin-ml2 neutron-plugin-openvswitch-agent \
  neutron-l3-agent neutron-dhcp-agent

### configure
file=/etc/neutron/neutron.conf
./openstack-config --set $file DEFAULT verbose True
./openstack-config --set $file DEFAULT rpc_backend rabbit
./openstack-config --set $file DEFAULT rabbit_host $CONTROLLER
./openstack-config --set $file DEFAULT rabbit_password $RABBIT_PASS
./openstack-config --set $file DEFAULT auth_strategy keystone
./openstack-config --set $file keystone_authtoken auth_uri $AUTH_URI
./openstack-config --set $file keystone_authtoken identity_uri $IDENTITY_URI
./openstack-config --set $file keystone_authtoken admin_tenant_name service
./openstack-config --set $file keystone_authtoken admin_user neutron
./openstack-config --set $file keystone_authtoken admin_password $NEUTRON_PASS
./openstack-config --set $file DEFAULT core_plugin ml2
./openstack-config --set $file DEFAULT service_plugins router
./openstack-config --set $file DEFAULT allow_overlapping_ips True

file=/etc/neutron/plugins/ml2/ml2_conf.ini
./openstack-config --set $file ml2 type_drivers flat,gre
./openstack-config --set $file ml2 tenant_network_types gre
./openstack-config --set $file ml2 mechanism_drivers openvswitch
./openstack-config --set $file ml2_type_gre flat_networks external
./openstack-config --set $file ml2_type_gre tunnel_id_ranges 1001:2000
./openstack-config --set $file securitygroup enable_security_group True
./openstack-config --set $file securitygroup enable_ipset True
./openstack-config --set $file securitygroup firewall_driver neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
./openstack-config --set $file ovs local_ip $INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS
./openstack-config --set $file ovs enable_tunneling True
./openstack-config --set $file ovs bridge_mappings external:br-ex
./openstack-config --set $file agent tunnel_types gre

file=/etc/neutron/l3_agent.ini
./openstack-config --set $file DEFAULT interface_driver neutron.agent.linux.interface.OVSInterfaceDriver
./openstack-config --set $file DEFAULT use_namespaces True
./openstack-config --set $file DEFAULT external_network_bridge br-ex
./openstack-config --set $file DEFAULT router_delete_namespaces True
./openstack-config --set $file DEFAULT verbose True

file=/etc/neutron/dhcp_agent.ini
./openstack-config --set $file DEFAULT dhcp_driver neutron.agent.linux.dhcp.Dnsmasq
./openstack-config --set $file DEFAULT interface_driver neutron.agent.linux.interface.OVSInterfaceDriver
./openstack-config --set $file DEFAULT use_namespaces True
./openstack-config --set $file DEFAULT dhcp_delete_namespaces True
./openstack-config --set $file DEFAULT verbose True

# prevent MTU problems
./openstack-config --set $file DEFAULT dnsmasq_config_file /etc/neutron/dnsmasq-neutron.conf
echo "dhcp-option-force=26,1454" > /etc/neutron/dnsmasq-neutron.conf

file=/etc/neutron/metadata_agent.ini
./openstack-config --set $file DEFAULT auth_url $AUTH_URI
./openstack-config --set $file DEFAULT auth_region $REGION
./openstack-config --set $file DEFAULT admin_tenant_name service
./openstack-config --set $file DEFAULT admin_user neutron
./openstack-config --set $file DEFAULT admin_password $NEUTRON_PASS
./openstack-config --set $file DEFAULT nova_metadata_ip $CONTROLLER
./openstack-config --set $file DEFAULT metadata_proxy_shared_secret $METADATA_SECRET
./openstack-config --set $file DEFAULT verbose True

pkill dnsmasq || true

# reconfigure OVS
service openvswitch-switch restart
ovs-vsctl add-br br-ex
ovs-vsctl add-port br-ex $EXTERNAL_INTERFACE
ethtool -K $EXTERNAL_INTERFACE gro off

# restart services
service neutron-plugin-openvswitch-agent restart
service neutron-l3-agent restart
service neutron-dhcp-agent restart
service neutron-metadata-agent restart
