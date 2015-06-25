#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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
author = 'chema'


class NovaResources(object):
    def __init__(self, osclients):
        self.novaclient = osclients.get_novaclient()
        self.tenant_id = osclients.get_session().get_project_id()

    def get_tenant_vms(self):
        vms = list()
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            vms.append((vm.id, vm.user_id))
        return vms

    def stop_tenant_vms(self):
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            if vm.status == 'ACTIVE':
                vm.stop()

    def delete_tenant_vms(self):
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            vm.delete()

    def get_user_keypairs(self):
        """Only is possible to obtain the keypairs of the user"""
        keypairs = list()
        for keypair in self.novaclient.keypairs.list():
            keypairs.append(keypair.id)
        return keypairs

    def delete_user_keypairs(self):
        for keypair in self.novaclient.keypairs.list():
            keypair.delete()

    def get_tenant_security_groups(self):
        """Only is possible to obtain the security groups of the tenant"""
        security_groups = list()

        for secgroup in self.novaclient.security_groups.list():
            # print secgroup.tenant_id, secgroup.id
            if secgroup.name == 'default' \
                    or secgroup.tenant_id != self.tenant_id:
                continue
            security_groups.append(secgroup.id)
        return security_groups

    def delete_tenant_security_groups(self):
        for secgroup in self.novaclient.security_groups.findall():
            if secgroup.name == 'default' \
                    or secgroup.tenant_id != self.tenant_id:
                continue
            secgroup.delete()
