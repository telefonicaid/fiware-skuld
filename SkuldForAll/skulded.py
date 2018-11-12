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
import re

REGION = 'Spain2'
JSON_DATA_FILE = '/tmp/outdated_people.json'
WHITE_LIST = 'whitelist.txt'

users = {}
projects = {}
whitelist = []

def build_whitelist():
    try:
        fd = open(WHITE_LIST)
        lines=fd.read().splitlines()
    
        fd.close()

        return lines
    except:
        return []


def match(user):
    anymatch=False

    s = user['email'] if user.has_key('email') and user['email'] is not None else user['name']

    for r in whitelist:
         if re.match(r, s, re.M|re.I):
              anymatch = True
              break

    return anymatch


def get_user_type(info):
        if not info.has_key('type'):
            user_type = 'NE'
        elif info['type'] == 'Community':
           user_type = 'C'
        elif info['type'] == 'Trial':
           user_type = 'T'
        else:
            user_type = 'E'
        return user_type


def is_project_removable(project, users):
    response = True
    if not project.has_key('Region') or project['Region'] != REGION:
        response = False
    elif project.has_key('users'):
        for u in project['users']:
            if match(users[u]):
                response = False
            if users[u].has_key('days_expired') and users[u]['days_expired'] <= 0:
                response = False
    else:
        response = False

    return response

def is_user_removable(user, projects):
    response = True
    if user.has_key('projects'):
        for p in user['projects']:
            if match(user):
                response = False
            if not projects.has_key(p):
                user['error'] = p + " is not a valid project"
            elif projects[p].has_key('removable') and projects[p]['removable'] == False:
                response = False
            elif user.has_key('days_expired') and user['days_expired'] <= 0:
                response = False
    else:
        response = False

    return response


if __name__ == '__main__':
    whitelist = build_whitelist()

    # Load JSON_DATA_FILE file, which should be the output of script "interesting_info.py"
    data = load_json_file(JSON_DATA_FILE)

    users = data['users']
    projects = data['projects']

    delete_or_not_delete = {}

    for pjid in projects:
        project = projects[pjid]
        project['removable'] = is_project_removable(project, users)

    for uid in users:
        user = users[uid]
        user['removable'] = is_user_removable(user, projects)

    print json.dumps(data)
