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

# CAVEATS:
# You must have set the openstack credentials (usually: "source openrc")
# before running this script.
#
# Please, be aware that this script is may not be correct with Organizations.
#
# This script creates the file /tmp/2delete.txt which is the script to use
# to delete the VMs of those people who haven't accepted terms and
# conditions
#
# Author: Chema

. config_vars

export DEBIAN_FRONTEND=noninteractive
echo mariadb-server-5.5 mysql-server/root_password password $MYSQL_PASS | debconf-set-selections
echo mariadb-server-5.5 mysql-server/root_password_again password $MYSQL_PASS | debconf-set-selections


apt-get install ubuntu-cloud-keyring
echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu" \
  "trusty-updates/juno main" > /etc/apt/sources.list.d/cloudarchive-juno.list

apt-get update && apt-get -y dist-upgrade

sudo apt-get install -y rabbitmq-server
apt-get -y install python-iniparse

cd $(dirname $0)
sudo apt-get -y install mariadb-server python-mysqldb
cat <<EOF |sudo tee /etc/mysql/conf.d/openstack.cnf >/dev/null
[mysqld]
default-storage-engine = innodb
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8
EOF
sudo service mysql restart

rabbitmqctl change_password guest $RABBIT_PASS