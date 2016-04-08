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

cd $(dirname $0)

# add alias to use nova with keystone URL v2
echo alias nova=\'env OS_AUTH_URL=\$OS_AUTH_URL_V2 nova\' > ~/.bash_aliases

# create properties file, register region
./keystone_work.sh

# install controller (this might be run in another node)
sudo ./prepare_controller.sh
sudo ./install_glance.sh


