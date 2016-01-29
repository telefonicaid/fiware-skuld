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

# Arbitray IP, but be aware that must be in $NEUTRON_IPS range.
IP_EXTDEV0=192.168.57.1/24
#apt-get update
#apt-get install -y openvpn
# TODO: this is a temporal workaround
ip tuntap add mode tap extdev0
ip address add dev extdev0 $IP_EXTDEV0
