#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2018 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##
 

__author__ = "Jose Ignacio Carretero Guarde"


import requests
import json
import re
import sys
import time
from functions import *
from ConfigParser import ConfigParser


class Config:
    def __init__(self, config_file):
        if config_file is None: 
            d = {"auth_url": os.environ.get('OS_AUTH_URL'), 
            "username": os.environ.get('OS_USERNAME'), 
            "password": os.environ.get('OS_PASSWORD'), 
            "project_name": os.environ.get('OS_PROJECT_NAME'), 
            "user_domain_id": os.environ.get('OS_USER_DOMAIN_ID'), 
            "project_id": os.environ.get('OS_PROJECT_ID'), 
            "project_domain_id": os.environ.get('OS_PROJECT_DOMAIN_ID')} 
        else:
            parser = ConfigParser()
            parser.read(config_file)
            d = {"auth_url": parser.get('keystone', 'url'),
            "username": parser.get('keystone', 'username'),
            "password": parser.get('keystone', 'password'),
            "project_name": parser.get('keystone', 'projectname'),
            "user_domain_id": 'default',
            "project_domain_id": 'default'} 
            if parser.has_section('neutron'):
                d['neutron_url'] = parser.get('neutron', 'url')
            if parser.has_section('nova'):
                d['nova_url'] = parser.get('nova', 'url')
            if parser.has_section('glance'):
                d['glance_url'] = parser.get('glance', 'url')
            if parser.has_section('monasca'):
                d['monasca_url'] = parser.get('monasca', 'url')
            if parser.has_section('cinder'):
                d['cinder_url'] = parser.get('cinder', 'url')
        self.__dict__.update(d)

    
class OpenstackQueries:
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.url = self.config.auth_url
        self.token = self.get_admin_token3()


    def get_admin_token3(self):
        """
        Get the token id based on the credentials.
        :return: Token id.
        """
        sys.stderr.write("Getting Admin token... %s\n" %
            sys._getframe().f_code.co_name)
    
        payload = {'auth':
            {'tenantName': self.config.project_name,
                'passwordCredentials': {'username': self.config.username, 'password': self.config.password}
            }
        }
    
        headers = {'content-type': 'application/json'}
        url = self.url + "/v2.0/tokens"
        r = requests.post(url=url, headers=headers, data=json.dumps(payload))

        return r.json()['access']['token']['id']
    
    
    
    def remove_elements_from_list_of_dicts(self, d, elements):
        """
        Given d a list of dictionaries or a dictionary itself, this 
        function will remove the keys given in parameter elements from
        the dictionary or from the list of dictionaries
        
        :return: d, the dictionary or list modified.
        """
        if type(d) is dict:
           d=[d]
    
        for l in d:
            for e in elements:
                if e in l:
                    del(l[e])
    
        return d
    
    
    def rename_elements_from_list_of_dicts(self, d, elements):
        """
        Given d a list of dictionaries or a dictionary itself, this 
        function will rename the keys given in parameter elements from
        the dictionary or from the list of dictionaries
        
        :return: d, the dictionary or list modified.
        """
        if type(d) is dict:
           d=[d]
    
        for l in d:
            for e in elements:
                if e[0] in l:
                    l[e[1]] = l[e[0]]
                    del(l[e[0]])
    
        return d
    
    
    # Refactorizar esto!!!
    def transform_elements_from_list_of_dicts(self, d, elements):
        """
        Given d a list of dictionaries or a dictionary itself, this 
        function will change things up all the way according to the
        array of tuples l
        
        The tuples are like this:
        (<outer_value>,<inner_value>,<new_outer_value>)
    
        This will remove d[<outer_value>] and will add the new elemente
        d[<new_outer_value>] witch will have the value of: 
          d[<outer_value>][<inner_value>]
        
        :return: d, the dictionary or list modified.
        """
        if type(d) is dict:
           d=[d]
    
        for l in d:
            for e in elements:
                if e[0] in l and e[1] in l[e[0]]:
                    v=l[e[0]][e[1]]
                    l[e[2]]=v
                    del(l[e[0]])
    
        return d
    
    
    def get_all_projects(self, token):
        """
        Queries all projects from Keystone
    
        :return: list of projects
        """
        sys.stderr.write("Getting projects ...\n")
    
        remove=['description', 'links', 'domain_id', 'website', 'city', 
                'img_small', 'img_original', 'img_medium', 'parent_id'] 
        url = self.url + '/v3/projects?include_names'
    
        return self.get_info_from_url(url, token, 
                                 tag='projects', 
                                 remove=remove)
    
    
    def get_all_users(self, token):
        """
        Queries all users from Keystone
    
        :return: list of users
        """
        sys.stderr.write("Getting users...\n")
    
        remove=['links','domain_id','aboutme', 'website']
        url = self.url + '/v3/users'
        return self.get_info_from_url(url, token, 
                                 tag='users',
                                 remove=remove)
    
    
    def get_all_endpoint_groups(self, token):
        """
        Queries all enpoint_groups from Keystone
    
        :return: list of endpoint groups
        """
        sys.stderr.write("Getting enpoint_groups ...\n")
    
        remove=['links','description']
        transform=[('filters','region_id','region_id')]
        url = self.url + '/v3/OS-EP-FILTER/endpoint_groups'
    
        return self.get_info_from_url(url, token, 
                                 tag='endpoint_groups',
                                 remove=remove,
                                 transform=transform)
    
    def get_all_endpoint_groups_projects(self, token, project_dict):
        """
        Queries all endpoint group for every project y project_dict
    
        :return: update project_dict
        """
        sys.stderr.write("Getting projects for every enpoint_group ...\n")
    
        url_base = self.url + '/v3/OS-EP-FILTER/endpoint_groups/'
        remove=['description', 'links', 'domain_id', 'website', 'city', 
                'img_small', 'img_original', 'img_medium'] 
    
        for i in project_dict:
           url=url_base+i['id']+'/projects'
           projects=self.get_info_from_url(url, token, 
                                      tag='projects',
                                      remove=remove)
           i['projects']=projects
    
        return project_dict
    
    
    def get_role_list(self, token):
        """
        Queries all the roles defined in the project
    
        :return: role list
        """
        
        sys.stderr.write("Getting role_list ...\n")
    
        remove=['links','domain']
        url = self.url + '/v3/roles?include_names'
        return self.get_info_from_url(url, token, 
                   tag='roles',
                   remove=remove)
    
    
    def get_role_assignment_list(self, token):
        """
        Queries all the roles assignments to every project.
    
        :return: role list
        """
        sys.stderr.write("Getting role_assignment_list ...\n")
    
        transforms=[('scope','project', 'scope_project'),
                    ('scope','domain', 'scope_domain'),
                    ('scope_project','id', 'scope_project_id'),
                    ('scope_domain','id', 'scope_domain_id'),
                    ('role','id', 'role_id'),
                    ('user','id', 'user_id'),
                    ('user','id', 'user_id')]
        remove=['links']
        url = self.url + '/v3/role_assignments?include_names'
        return self.get_info_from_url(url, token, 
                   tag='role_assignments',
                   remove=remove,
                   transform=transforms)

    def get_service_providers_config(self, token):
        """
        Queries the sum of Keyrock

        :return: the sum up of things to put in monasca
        """
        sys.stderr.write("get_service_providers_config for keyrock\n")
        url = self.url + '/v3/OS-SCIM/v2/ServiceProviderConfigs'
        return self.get_info_from_url(url, token)
        #           tag='service_providers_config')

        
    
    def get_all_servers(self, token):
        sys.stderr.write("Getting all servers ...\n")
        url = 'http://130.206.112.3:8774/v2/00000000000003228460960090160000/servers/detail?all_tenants=True'
        remove=['links','OS-SRV-USG:terminated_at','OS-EXT-AZ:availability_zone','hostId',
                'metadata','OS-EXT-STS:task_state','security_groups','OS-DCF:diskConfig',
                'os-extended-volumes:volumes_attached','accessIPv4','accessIPv6','progress',
                'OS-EXT-STS:power_state','OS-EXT-SRV-ATTR:host','config_drive']
        transforms=[('image','id','image_id'),
                    ('flavor','id','flavor_id')]
        rename=[('OS-EXT-STS:vm_state','vm_state'),
                ('OS-EXT-SRV-ATTR:instance_name','virsh_name'),
                ('OS-SRV-USG:launched_at','launched_at'),
                ('OS-EXT-SRV-ATTR:hypervisor_hostname','hypervisor_hostname')]
        return self.get_info_from_url(url, token, 
                                 tag='servers',
                                 remove=remove,
                                 transform=transforms,
                                 rename=rename)
    
    def get_all_volumes(self, token):
        sys.stderr.write("Getting all volumes ...\n")
        url = self.config.cinder_url
        remove = ['links','volume_image_metadata','os-vol-mig-status-attr:name_id',
                  'os-volume-replication:driver_data','availability_zone','os-volume-replication:extended_status',
                  'metadata']
        rename = [('os-vol-tenant-attr:tenant_id','project_id')]
        return self.get_info_from_url(url, token, tag='volumes', remove=remove, rename=rename)

    
    def get_all_routers(self, token):
        sys.stderr.write("Getting all routers ...\n")
        url = self.config.neutron_url + "/v2.0/routers.json"
        return self.get_info_from_url(url, token, 
                                 tag='routers')

    def get_all_ports(self, token):
        sys.stderr.write("Getting all ports ...\n")
        url = self.config.neutron_url+"/v2.0/ports.json"
        return self.get_info_from_url(url, token, 
                                 tag='ports')
    
    
    def get_all_networks(self, token):
        sys.stderr.write("Getting all networks ...\n")
        url = self.config.neutron_url + "/v2.0/networks.json"
        return self.get_info_from_url(url, token, 
                                 tag='networks')
    
    
    def get_all_images(self, token):
        sys.stderr.write("Getting all images ...\n")
        url = self.config.glance_url + "/v2/images?limit=10000"
        return self.get_info_from_url(url, token, 
                                 tag='images')
    

    def get_info_from_url(self, url, token, **kargs):
        """
        Makes the select.
        """
        try:
            headers = {'x-auth-token': token}
            r = requests.get(url=url, headers=headers)
        except e:
            sys.stderr.write("..... exception found!!\n")
            headers = {'x-auth-token': token}
            r = requests.get(url=url, headers=headers)
    
        if 'tag' in kargs:
            result = r.json()[kargs['tag']]
        else:
            result = r.json()
        if 'remove' in kargs:
            self.remove_elements_from_list_of_dicts(result, kargs['remove'])
    
        if 'rename' in kargs:
            self.rename_elements_from_list_of_dicts(result, kargs['rename'])
    
        if 'transform' in kargs:
            self.transform_elements_from_list_of_dicts(result,  kargs['transform'])
    
        return result
