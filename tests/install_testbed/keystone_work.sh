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

# This scripts do all the operations that are not responsability of the
# region.

# prepare and activate virtualenv
virtualenv ~/skuldenv
. ~/skuldenv/bin/activate

# update repository & install pwgen
sudo apt-get update
sudo apt-get install -y pwgen

pip install -r ~/fiware-skuld/requirements.txt --allow-all-external
pip install python-openstackclient


export PYTHONPATH=~/fiware-skuld

# create properties
./generate_region_config.py

# change idm default password & generate new credential
./change_idm_password.py

# register region data and create service project if it does not exist
. config_vars
. ~/credential
./register_region.py

# append tenant id of service to configuration file
get_tenant_id() {
cat <<EOF | python
from utils.osclients import osclients
print osclients.get_keystoneclient().projects.find(name="$1").id,
EOF
}
echo "export SERVICE_TENANT_ID=$(get_tenant_id service)" >> config_vars
