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
# Authors: Jose Ignacio Carretero Guarde and Chema

. config_vars

MY_IP=`ip a| awk "/inet $MANAGEMENT_IPS/  {print gensub(/\/../,\"\",\"g\",\\$2)}"`

## create the database
./create_mysqldb $NOVA_DB $NOVA_DBPASSWORD

## install the packages
apt-get install -y nova-api nova-cert nova-conductor nova-consoleauth \
  nova-novncproxy nova-scheduler python-novaclient

## configure
file=/etc/nova/nova.conf
./openstack-config --set $file database connection mysql://$NOVA_DBUSER:$NOVA_DBPASSWORD@$CONTROLLER/$NOVA_DB
./openstack-config --set $file DEFAULT rpc_backend rabbit
./openstack-config --set $file DEFAULT rabbit_host $CONTROLLER
./openstack-config --set $file DEFAULT rabbit_password $RABBIT_PASS
./openstack-config --set $file DEFAULT auth_strategy keystone
./openstack-config --set $file DEFAULT my_ip $MY_IP
./openstack-config --set $file DEFAULT vncserver_listen 0.0.0.0
./openstack-config --set $file DEFAULT vncserver_proxyclient_address $MY_IP
./openstack-config --set $file DEFAULT verbose True
./openstack-config --set $file keystone_authtoken auth_uri $AUTH_URI
./openstack-config --set $file keystone_authtoken identity_uri $IDENTITY_URI
./openstack-config --set $file keystone_authtoken admin_tenant_name service
./openstack-config --set $file keystone_authtoken admin_user nova$REGION
./openstack-config --set $file keystone_authtoken admin_password $NOVA_PASS
./openstack-config --set $file glance host $CONTROLLER

## populate the database
su -s /bin/sh -c "nova-manage db sync" nova

# restart services
service nova-api restart
service nova-cert restart
service nova-consoleauth restart
service nova-scheduler restart
service nova-conductor restart
service nova-novncproxy restart
