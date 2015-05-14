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
neutron = osclients.get_neutronclient()



def get_tenant_floatingips(tenant_id=None):
    floatingips = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for floatingip in neutron.list_floatingips()['floatingips']:
        if floatingip['tenant_id'] != tenant_id:
            continue

        floatingips.append(floatingip['id'])
    return floatingips

def delete_tenant_floatingips(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for floatingip in neutron.list_floatingips()['floatingips']:
        if floatingip['tenant_id'] != tenant_id:
            continue

        neutron.delete_floatingip(floatingip['id'])

def get_tenant_networks(tenant_id=None):
    networks = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for net in neutron.list_networks()['networks']:
        if net['tenant_id'] != tenant_id:
            continue

        networks.append((net['id'], net['shared']))
    return networks

def delete_tenant_networks(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for net in neutron.list_networks()['networks']:
        if net['tenant_id'] != tenant_id:
            continue

        neutron.delete_network(net['id'])

def get_tenant_subnets(tenant_id=None):
    subnets = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for subnet in neutron.list_subnets()['subnets']:
        if subnet['tenant_id'] != tenant_id:
            continue

        subnets.append((subnet['tenant_id'], subnet['id']))
    return subnets

def delete_tenant_subnets(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for subnet in neutron.list_subnets()['subnets']:
        if subnet['tenant_id'] != tenant_id:
            continue

        neutron.delete_subnet(subnet['id'])


def get_tenant_routers(tenant_id=None):
    routers = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for router in neutron.list_routers()['routers']:
        if router['tenant_id'] != tenant_id:
            continue

        routers.append(router['id'])
    return routers

def delete_tenant_routers(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for router in neutron.list_routers()['routers']:
        if router['tenant_id'] != tenant_id:
            continue

        neutron.remove_gateway_router(router['id'])
        neutron.delete_router(router['id'])


def get_tenant_securitygroups(tenant_id=None):
    securitygroups = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for security_group in neutron.list_security_groups()['security_groups']:
        if security_group['tenant_id'] != tenant_id:
            continue
        if security_group['name'] == 'default':
            continue
        securitygroups.append(security_group['id'])
    return securitygroups

def delete_tenant_securitygroups(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for security_group in neutron.list_security_groups()['security_groups']:
        if security_group['tenant_id'] != tenant_id:
            continue
        if security_group['name'] == 'default':
            continue

        neutron.delete_security_group(security_group['id'])

def get_tenant_ports(tenant_id=None):
    ports = list()
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for port in neutron.list_ports()['ports']:
        if port['tenant_id'] != tenant_id:
            continue
        ports.append(port['id'])
    return ports

def delete_tenant_ports(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()
    for port in neutron.list_ports()['ports']:
        if port['tenant_id'] != tenant_id:
            continue
        #if port['device_owner'] == 'network:router_interface':
        #    neutron.remove_interface_router(router=port['device_id'], )
        else:
            neutron.delete_port(port['id'])
