#!/bin/bash -xe
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

# create database
./create_mysqldb $GLANCE_DB $GLANCE_DBPASSWORD

### install packages
apt-get -y install glance python-glanceclient

### configure
file=/etc/glance/glance-api.conf
./openstack-config --set $file database connection mysql://$GLANCE_DBUSER:$GLANCE_DBPASSWORD@$CONTROLLER/$GLANCE_DB
./openstack-config --set $file keystone_authtoken auth_uri $AUTH_URI
./openstack-config --set $file keystone_authtoken identity_uri $IDENTITY_URI
./openstack-config --set $file keystone_authtoken admin_tenant_name service
./openstack-config --set $file keystone_authtoken admin_user glance
./openstack-config --set $file keystone_authtoken admin_password $GLANCE_PASS
./openstack-config --set $file paste_deploy flavor keystone
./openstack-config --set $file glance_store default_store file
./openstack-config --set $file glance_store filesystem_store_datadir /var/lib/glance/images/
./openstack-config --set $file DEFAULT notification_driver noop
./openstack-config --set $file DEFAULT verbose True

file=/etc/glance/glance-registry.conf
./openstack-config --set $file database connection mysql://$GLANCE_DBUSER:$GLANCE_DBPASSWORD@$CONTROLLER/$GLANCE_DB
./openstack-config --set $file keystone_authtoken auth_uri $AUTH_URI
./openstack-config --set $file keystone_authtoken identity_uri $IDENTITY_URI
./openstack-config --set $file keystone_authtoken admin_tenant_name service
./openstack-config --set $file keystone_authtoken admin_user glance
./openstack-config --set $file keystone_authtoken admin_password $GLANCE_PASS
./openstack-config --set $file paste_deploy flavor keystone
./openstack-config --set $file DEFAULT notification_driver noop
./openstack-config --set $file DEFAULT verbose True


### populate the database
su -s /bin/sh -c "glance-manage db_sync" glance
rm -f /var/lib/glance/glance.sqlite

service glance-registry restart
service glance-api restart
