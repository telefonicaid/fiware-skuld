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

import logging

from osclients import osclients
import openstackmap
from settings.settings import TRIAL_ROLE_ID, COMMUNITY_ROLE_ID, BASIC_ROLE_ID,\
    ADMIN_ROLE_ID
import utils.log
import sys
import argparse


class ClassifyResources(object):
    """Class to analyse the resources by owner, for discovering resources
       belonging to users that should not have resources, or resources without
       an owner"""

    def __init__(self, cache_dir, regions=None):
        """Constructor
        It also build the sets about users and tenants
        :param cache_dir: the directory where the data is cached.
        :param regions: a list with the regions whose maps are preload. If None
          all the available regions.
        """
        self.logger = logging.getLogger(__name__)
        if regions:
            self.map = openstackmap.OpenStackMap(cache_dir, auto_load=False)
            self.map.preload_regions(regions)
        else:
            self.map = openstackmap.OpenStackMap(cache_dir)

        # This groups should be disjoint
        self.admin_users = set()
        self.trial_users = set()
        self.community_users = set()
        self.basic_users = set()
        self.other_users = set()
        self.not_found_users = set()
        # Broken users can be of any of the other types (not found, basic...)
        self.broken_users = set()

        self.user_cloud_projects = set()
        self.user_default_projects = set()

        self.comtrialadmin_cloud_projects = set()
        self.basic_cloud_projects = set()
        self.community_cloud_projects = set()
        self.trial_cloud_projects = set()
        self.admin_cloud_projects = set()
        self.other_users_cloud_projects = set()
        self.not_found_cloud_projects = set()
        self.broken_users_projects = set()

        self._process_users()

    def _process_users(self):
        projects = set(self.map.tenants.keys())
        for user in self.map.users.values():

            if 'cloud_project_id' in user:
                cloud_project_id = user.cloud_project_id
                self.user_cloud_projects.add(cloud_project_id)
                if user.cloud_project_id not in projects:
                    self.broken_users.add(user.id)
                    self.broken_users_projects.add(cloud_project_id)
            else:
                cloud_project_id = None

            if 'default_project_id' in user:
                self.user_default_projects.add(user.default_project_id)

            if user.id not in self.map.roles_by_user:
                self.not_found_users.add(user.id)
                if cloud_project_id:
                    self.not_found_cloud_projects.add(cloud_project_id)
                continue

            roles = self.map.roles_by_user[user.id]
            user_type = None
            for rol in roles:
                if rol[0] == BASIC_ROLE_ID:
                    user_type = 'basic'
                    self.basic_users.add(user.id)
                    if cloud_project_id:
                        self.basic_cloud_projects.add(cloud_project_id)
                elif rol[0] == COMMUNITY_ROLE_ID:
                    user_type = 'community'
                    self.community_users.add(user.id)
                    if cloud_project_id:
                        self.community_cloud_projects.add(cloud_project_id)
                elif rol[0] == TRIAL_ROLE_ID:
                    user_type = 'trial'
                    self.trial_users.add(user.id)
                    if cloud_project_id:
                        self.trial_cloud_projects.add(cloud_project_id)
                elif rol[0] == ADMIN_ROLE_ID:
                    user_type = 'admin'
                    self.admin_users.add(user.id)
                    # use default_project_id with admin users, because
                    # cloud_project_id does not exist.
                    self.admin_cloud_projects.add(user.default_project_id)
                    self.user_cloud_projects.add(cloud_project_id)

            if not user_type:
                self.other_users.add(user.id)
                if cloud_project_id:
                    self.other_users_cloud_projects.add(cloud_project_id)

        self.comtrialadmin_cloud_projects.update(self.community_cloud_projects)
        self.comtrialadmin_cloud_projects.update(self.trial_cloud_projects)
        self.comtrialadmin_cloud_projects.update(self.admin_cloud_projects)

        if self.basic_users.intersection(self.admin_users):
            self.logger.error('There are users both in admin and basic')
        if self.basic_users.intersection(self.community_users):
            msg = 'There are users both in community and basic'
            self.logger.error(msg)
        if self.basic_users.intersection(self.trial_users):
            self.logger.error('There are users both in trial and basic')
        if self.community_users.intersection(self.trial_users):
            msg = 'There are users both in community and trial'
            self.logger.error(msg)
        if self.community_users.intersection(self.admin_users):
            msg = 'There are users both in community and admin'
            self.logger.error(msg)
        if self.trial_users.intersection(self.admin_users):
            self.logger.error('There are users both in admin and trial')

    def print_users_summary(self):
        print
        print 'Total users: ', len(self.map.users)
        print '---- Users by type:'
        print 'Basic users: ', len(self.basic_users)
        print 'Community users: ', len(self.community_users)
        print 'Trial users: ', len(self.trial_users)
        print 'Admin users: ', len(self.admin_users)
        print 'Other type users: ', len(self.other_users)
        print 'Users without type: ', len(self.not_found_users)
        print '----'
        print 'Users with a project-id that does not exist: ', \
            len(self.broken_users)
        print

    def classify_resource(self, member, region=None):
        special_cases = {'images': 'owner',
                         'volumes': 'os-vol-tenant-attr:tenant_id',
                         'volume_snapshots':
                             'os-extended-snapshot-attributes:project_id',
                         'volume_backups':
                             'os-extended-snapshot-attributes:project_id'}
        if region and self.map.osclients.region != region:
            if region in self.map.region_map:
                elements = self.map.region_map[region][member]
            else:
                self.map.change_region(region)
                elements = getattr(self.map, member)
        else:
            elements = getattr(self.map, member)
            region = self.map.osclients.region



        if member in special_cases:
            attr = special_cases[member]
            for element in elements.values():
                element['tenant_id'] = element[attr]
        print '==Resources: {0}. Region: {1} '.format(member, region)
        print 'Total:', len(elements)
        return self.classify_resource_raw(elements)

    def classify_resource_raw(self, element_list):
        owned = list()
        unkown_owner = list()
        unkown_tenant = list()

        ok = 0
        community = 0
        trial = 0
        admin = 0
        basic = 0
        other_type = 0
        unknown_type = 0
        default_project_id = 0

        for element in element_list.values():
            tenant_id = element['tenant_id']
            if tenant_id in self.comtrialadmin_cloud_projects:
                ok += 1
                if tenant_id in self.community_cloud_projects:
                    community += 1
                elif tenant_id in self.trial_cloud_projects:
                    trial += 1
                else:
                    admin += 1
            elif tenant_id in self.user_cloud_projects:
                owned.append(element)
                if tenant_id in self.basic_cloud_projects:
                    basic += 1
                elif tenant_id in self.other_users_cloud_projects:
                    other_type += 1
                else:
                    unknown_type += 1

            elif tenant_id in self.map.tenants:
                if tenant_id in self.user_default_projects:
                    default_project_id += 1
                unkown_owner.append(element)
            else:
                unkown_tenant.append(element)

        msg = 'Owned by users community/trial/admin: {0} ({1}/{2}/{3})'
        print msg.format(ok, community, trial, admin)
        msg = 'Owned by users basic/other type/unknown type: {0} ({1}/{2}/{3})'
        print msg.format(len(owned), basic, other_type, unknown_type)
        m = 'Owned by another projects id: {0} (using default_project_id {1})'
        print m.format(len(unkown_owner), default_project_id)
        print 'Project id does not exist:', len(unkown_tenant)

        return owned, unkown_owner, unkown_tenant


class hidden_set(set):
    def __init__(self, baselist):
        super(hidden_set, self).__init__(baselist)
        self.hidden_set = set()
        self.baselist = baselist

    def add_hidden(self, hidden):
        self.hidden_set.add(hidden)

    def __contains__(self, element):
        return super(hidden_set, self).__contains__(element) or\
            element in self.hidden_set

    def to_list(self):
        return self.baselist

if __name__ == '__main__':
    logger = utils.log.init_logs('classify_resources_by_owner')
    # Parse cmdline
    description = 'A tool to classify users and the resources on any region'
    parser = argparse.ArgumentParser(description=description)

    res_types = hidden_set(openstackmap.OpenStackMap.resources_region)
    res_types.add_hidden('none')
    res_types.add_hidden('all')

    h = 'resources to analyse. If may be all or any of this list: %(choices)s'
    parser.add_argument('resources', metavar='resource', type=str, nargs='*',
                        choices=res_types, default='none', help=h)

    parser.add_argument('--regions', nargs='+', help='regions to analyse')

    parser.add_argument('--omit-user-summary', action='store_true',
                        help='do not print the summary about user types')
    help='data is cached in this directory (default is %(default)s)'
    parser.add_argument('--cache-dir', help=help, default='~/openstackmap')

    meta = parser.parse_args()

    if meta.regions:
        object = ClassifyResources(meta.cache_dir, meta.regions)
    else:
        object = ClassifyResources(meta.cache_dir)

    if not meta.omit_user_summary:
        object.print_users_summary()

    if meta.resources == 'none':
        sys.exit(0)

    if 'all' in meta.resources:
        meta.resources = res_types.to_list()

    if meta.regions:
        for region in meta.regions:
            for resource in meta.resources:
                object.classify_resource(resource, region)
    else:
        for resource in meta.resources:
            object.classify_resource(resource)
