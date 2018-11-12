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


from functions import *
import json
import sys

REGION = 'Spain2'
JSON_DATA_FILE = '/tmp/all.json'

DEFAULT_COMMUNITY_DURATION = 270
DEFAULT_TRIAL_DURATION = 15

def get_role_ids(data, role_name):
    return [x['id'] for x in data['roles'] if x['name'] == role_name][0]


def get_region_project_ids(data):
    # Get Region's projects from "endpoint_groups" info
    region_projects = [x['projects'] for x in data['endpoint_groups'] 
            if x.has_key('region_id') and x['region_id'] == REGION][0]

    # Get an array with project ids in noida. This will help to filter later
    return [x['id'] for x in region_projects]


def get_region_userids_for_projects(data, region_project_ids):
    # Filter role assignmets for Regions's projects - roles (list(set(... --- to remove duplicate entries
    region_role_assignments = [x for x in data['role_assignments'] 
            if x.has_key('scope_project_id') and x['scope_project_id'] in region_project_ids]

    # Get an array with users for Region's project --- 
    return list(set([x['user_id'] for x in region_role_assignments]))


def get_user_ids(data):
    # Get Region users dict by user_id --- Easier to query
    user_ids = get_dict_from_data(data, 'users', 'id')
    project_ids = get_dict_from_data(data, 'projects', 'id')

    # Fill user_ids with projects they belong to --- just to be queried later
    for assignment in data['role_assignments']:
        if assignment.has_key('scope_project_id'):
            user = assignment['user_id']
            project = assignment['scope_project_id']

            # We fill user_ids with projects
            if user_ids.has_key(user):
                if not user_ids[user].has_key('projects'):
                    user_ids[user]['projects'] = []

                if not project in user_ids[user]['projects']:
                    user_ids[user]['projects'].append(project)

            # We fill project_ids with users
            if user_ids.has_key(user):
                if not project_ids[project].has_key('users'):
                    project_ids[project]['users'] = []

                if not user in project_ids[project]['users']:
                    project_ids[project]['users'].append(user)

    return user_ids, project_ids


if __name__ == '__main__':

    if len(sys.argv) > 1:
        output_type = sys.argv[1]
    else:
        output_type = "text"

    # Load JSON_DATA_FILE file, which should be the output of script "interesting_info.py"
    data = load_json_file(JSON_DATA_FILE)

    # Get Trial an Community roles IDs
    trial_role_id = get_role_ids(data, 'trial')
    community_role_id = get_role_ids(data, 'community')

    # Get List of Project IDs assigned to the region REGION
    region_project_ids = get_region_project_ids(data)


    region_users = get_region_userids_for_projects(data, region_project_ids)

    # Get trial role_assignments
    trial_users = [x['user_id'] for x in data['role_assignments'] 
            if x.has_key('scope_domain_id') and x['role_id'] == trial_role_id and x['user_id'] in region_users]

    # Get community role_assignments
    community_users = [x['user_id'] for x in data['role_assignments'] 
            if x.has_key('scope_domain_id') and x['role_id'] == community_role_id and x['user_id'] in region_users]


    user_ids, project_ids = get_user_ids(data)

    for pjid in region_project_ids:
        project_ids[pjid]['Region'] = REGION

    for user in trial_users:
        try:
            duration = user_ids[user]['trial_duration'] \
                    if user_ids[user].has_key('trial_duration') else DEFAULT_TRIAL_DURATION
            creation_date = str_to_date(user_ids[user]['trial_started_at'])
            days = days_expired(creation_date, duration)
            user_ids[user]['days_expired'] = days
            email = user_ids[user]['email'] if user_ids[user].has_key('email') else user_ids[user]['name']
            user_ids[user]['type'] = 'Trial'
            if output_type != "json":
                print "T", user, user_ids[user]['trial_started_at'], duration, days, \
                        email, len(user_ids[user]['projects'])
        except Exception as e:
            sys.stderr.write("ERROR trial_users:"+ user +  str(e) + "\n")

    for user in community_users:
        try:
            duration = user_ids[user]['community_duration'] \
                    if user_ids[user].has_key('community_duration') else DEFAULT_COMMUNITY_DURATION
            creation_date = str_to_date(user_ids[user]['community_started_at'])
            days = days_expired(creation_date, duration)
            user_ids[user]['days_expired'] = days
            email = user_ids[user]['email'] if user_ids[user].has_key('email') else user_ids[user]['name']
            user_ids[user]['type'] = 'Community'
            if output_type != "json":
                print "C", user, user_ids[user]['community_started_at'], duration, days, \
                      email, len(user_ids[user]['projects'])
        except Exception as e:
            sys.stderr.write("ERROR community_users:"+ user + str(e) + "\n")

    if output_type == "json":
        output = {"users": user_ids, "projects": project_ids}
        # print(json.dumps(output))
        print json.dumps(output)
