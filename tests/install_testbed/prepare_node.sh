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
