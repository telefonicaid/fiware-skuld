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

import osclients

"""All data is obtained for all the tenants that has access (for a normal user
this includes the shared resources of other tenants"""

class NeutronResources(object):
    def __init__(self, osclients):
          self.neutron = osclients.get_neutronclient()
          self.tenant_id = osclients.get_session().get_project_id()

    def get_tenant_floatingips(self):
        floatingips = list()
        for floatingip in self.neutron.list_floatingips()['floatingips']:
            if floatingip['tenant_id'] != self.tenant_id:
                continue

            floatingips.append(floatingip['id'])
        return floatingips


    def delete_tenant_floatingips(self):
        for floatingip in self.neutron.list_floatingips()['floatingips']:
            if floatingip['tenant_id'] != self.tenant_id:
                continue

            self.neutron.delete_floatingip(floatingip['id'])


    def get_tenant_networks(self):
        networks = list()
        for net in self.neutron.list_networks()['networks']:
            if net['tenant_id'] != self.tenant_id:
                continue

            networks.append((net['id'], net['shared']))
        return networks


    def delete_tenant_networks(self):
        for net in self.neutron.list_networks()['networks']:
            if net['tenant_id'] != self.tenant_id:
                continue

            self.neutron.delete_network(net['id'])


    def get_tenant_subnets(self):
        subnets = list()
        for subnet in self.neutron.list_subnets()['subnets']:
            if subnet['tenant_id'] != self.tenant_id:
                continue

            subnets.append((subnet['tenant_id'], subnet['id']))
        return subnets


    def delete_tenant_subnets(self):
        for subnet in self.neutron.list_subnets()['subnets']:
            if subnet['tenant_id'] != self.tenant_id:
                continue

            self.neutron.delete_subnet(subnet['id'])


    def get_tenant_routers(self):
        routers = list()
        for router in self.neutron.list_routers()['routers']:
            if router['tenant_id'] != self.tenant_id:
                continue

            routers.append(router['id'])
        return routers


    def delete_tenant_routers(self):
        for router in self.neutron.list_routers()['routers']:
            if router['tenant_id'] != self.tenant_id:
                continue

            self.neutron.remove_gateway_router(router['id'])
            self.neutron.delete_router(router['id'])


    def get_tenant_securitygroups(self):
        securitygroups = list()
        for security_group in self.neutron.list_security_groups()[
                'security_groups']:
            if security_group['tenant_id'] != self.tenant_id:
                continue
            if security_group['name'] == 'default':
                continue
            securitygroups.append(security_group['id'])
        return securitygroups


    def delete_tenant_securitygroups(self):
        for security_group in self.neutron.list_security_groups()[
                'security_groups']:
            if security_group['tenant_id'] != self.tenant_id:
                continue
            if security_group['name'] == 'default':
                continue

            self.neutron.delete_security_group(security_group['id'])


    def get_tenant_ports(self):
        ports = list()
        for port in self.neutron.list_ports()['ports']:
            if port['tenant_id'] != self.tenant_id:
                continue
            ports.append(port['id'])
        return ports


    def delete_tenant_ports(self):
        for port in self.neutron.list_ports()['ports']:
            if port['tenant_id'] != self.tenant_id:
                continue
            if port['device_owner'] == 'network:router_interface':
                subnet = port['fixed_ips'][0]['subnet_id']
                body = {'subnet_id': subnet}
                self.neutron.remove_interface_router(
                    router=port['device_id'], body=body)
            else:
                self.neutron.delete_port(port['id'])
