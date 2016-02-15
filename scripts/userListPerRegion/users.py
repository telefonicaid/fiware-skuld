#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
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
"""Get the users list of a specific FIWARE Lab region.

Usage:
  users --user=<username> --pass=<password> --region=<region> [--out=<filename>]
  users -h | --help
  users -v | --version

Options:
  -h --help           Show this screen.
  -v --version        Show version.
  -o --out=<filename> Store the information if the file <filename>.
  --user=<username>   Admin user that request the data.
  --pass=<password>   Admin password of the user.
  --region=<region>   Region name that we want to recover the information.

"""

author = 'fla'

from docopt import docopt
import requests
import os
import json

__version__ = '1.0.0'

KEYSTONE_URL = 'http://cloud.lab.fiware.org:4730'
API_V2 = 'v2.0'
API_V3 = 'v3'
TOKENS = 'tokens'
CONTENT_TYPE = 'application/json'
ACCEPT = CONTENT_TYPE
ENDPOINT_GROUPS = 'OS-EP-FILTER/endpoint_groups'
PROJECT_DETAILS = '%s/projects'
ROLE_ASSIGNMENT = 'role_assignments?scope.project.id=%s'
USER_DETAILS = 'users/%s'

def gettoken(username, password):
    """
    Get the admin token of a corresponding region administrator.

    :param username: the admin user name
    :param password: the admin password
    :return: the authenticated token
    """
    print('\nGetting administrator token...')

    body = '''
    {
        "auth": {
            "tenantName": "admin",
            "passwordCredentials": {
                "username": "%s",
                "password": "%s"
            }
        }
    }
    ''' % (username, password)

    url = os.path.join(KEYSTONE_URL, API_V2, TOKENS)
    headers = {'content-type': CONTENT_TYPE, 'accept': ACCEPT}

    response = requests.post(url=url, headers=headers, data=body)

    info = json.loads(response.text)
    token = info['access']['token']['id']

    return token

def getregionid(token, region):
    """
    Get the corresponding id of the region to check.

    :param token: The admin token.
    :param region: The region to get the id.
    :return: the id of the region.
    """
    print('Getting id of the requested region...')

    url = os.path.join(KEYSTONE_URL, API_V3, ENDPOINT_GROUPS)

    headers = {'X-Auth-Token': token}

    response = requests.get(url=url, headers=headers)

    info = json.loads(response.text)

    listregions = dict()

    for i in range(0, len(info['endpoint_groups'])):
        index = info['endpoint_groups'][i]
        filters = index['filters']
        if 'region_id' in filters:
            key = filters['region_id']
            value = index['id']

            listregions[key] = value

    return listregions[region]

def getprojectlist(token, regionid):
    """
    Get the list of projects in a specific region.

    :param token: The admin token.
    :param regionid: The region id to request projects.
    :return: The list of projects in that region.
    """
    print('Getting the list of projects in the specific region...')

    project_details = PROJECT_DETAILS % regionid
    url = os.path.join(KEYSTONE_URL, API_V3, ENDPOINT_GROUPS, project_details)

    headers = {'X-Auth-Token': token}

    response = requests.get(url=url, headers=headers)

    info = json.loads(response.text)

    listprojects = []

    for i in range(0, len(info['projects'])):
        listprojects.append(info['projects'][i]['id'])

    return listprojects

def getuserlist(token, projectlist):
    """
    Get the user list with some role in the list of projects.

    :param token: The Admin Token
    :param projectlist: The list of projects to requests users.
    :return: The list of users with some role in those projects.
    """
    print('Get the list of users with some role on those projects...')

    userlist = []

    for i in projectlist:
        role_assignment = ROLE_ASSIGNMENT % i
        url = os.path.join(KEYSTONE_URL, API_V3, role_assignment)

        headers = {'X-Auth-Token': token}

        response = requests.get(url=url, headers=headers)

        info = json.loads(response.text)

        for j in range(0, len(info['role_assignments'])):
            userlist.append(info['role_assignments'][j]['user']['id'])

    # we have to delete the repeat user from the list
    userset = set(userlist)

    return userset

def getemail(token, userset):
    """
    Get the list of users with their email.

    :param token: The admin token.
    :param userset: The set of users.
    :return: The dict of user name, user email.
    """
    print('Getting the email of the identified users...')

    useremail = dict()
    for i in userset:
        user_details = USER_DETAILS % i
        url = os.path.join(KEYSTONE_URL, API_V3, user_details)

        headers = {'X-Auth-Token': token}

        response = requests.get(url=url, headers=headers)

        info = json.loads(response.text)

        useremail[i] = info['user']['name']

    return useremail


def processingrequest(params):
    """
    Method to process the arguments received from the CLI and obtain the list of GE(r)i nids.
    :param params: Arguments received from the CLI.
    :return: A string format with the different GE(r)i and nids classified by chapter. If the --wikitext argument is
             specified, the method returns the data in tikiwiki format, nevertheless it returns in a dictionary
             representation.
    """
    username = params['--user']
    password = params['--pass']
    region = params['--region']

    token = gettoken(username, password)
    regionid = getregionid(token, region)
    projectlist = getprojectlist(token, regionid)
    userset = getuserlist(token, projectlist)
    useremail = getemail(token, userset)

    return useremail


if __name__ == '__main__':
    version = "Get users list of one region v{}".format(__version__)
    arguments = docopt(__doc__, version=version)

    output_file = arguments['--out']

    getusers = processingrequest(arguments)

    pretty_getusers = json.dumps(getusers, indent=4, separators=(',', ': '))

    if output_file is None:
        print('\n\n')
        print(pretty_getusers)
    else:
        f = open(output_file,"a")
        f.write(pretty_getusers)
        f.close()
