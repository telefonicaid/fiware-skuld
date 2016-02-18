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
from skuld.openstackmap import OpenStackMap

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
USER_DETAILS = 'users'


def get_token(username, password):
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


def get_endpoint_groups_id(token, region):
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


def get_project_list(token, regionid):
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


def get_user_list(token, projectlist):
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


def get_email(token, userset):
    """
    Get the list of users with their email.

    :param token: The admin token.
    :param userset: The set of users.
    :return: The dict of user name, user email.
    """
    print('Getting the email of the identified users...')

    useremail = dict()

    url = os.path.join(KEYSTONE_URL, API_V3, USER_DETAILS)
    headers = {'X-Auth-Token': token}

    response = requests.get(url=url, headers=headers)

    info = json.loads(response.text)

    # Delete unnecessary keys
    for i in range(0, len(info['users'])):
        user = info['users'][i]
        useremail[user['id']] = user['name']

    result = {k: useremail[k] for k in (useremail.viewkeys() & userset)}

    return result


def get_email_osclient(username, password, region):
    """
    Get the list of user of one region taking into account a bottom-up analysis.

    :param username: The name of the admin user that launch the request.
    :param password: The password of the admin user.
    :param region: The region in which we want to obtain the data.
    :return: The emaillist.
    """
    print("Making analysis bottom-up...")

    # Set environment variables
    os.environ['OS_USERNAME'] = username
    os.environ['OS_PASSWORD'] = password
    os.environ['OS_TENANT_NAME'] = 'admin'
    os.environ['OS_REGION_NAME'] = region
    os.environ['KEYSTONE_ADMIN_ENDPOINT'] = 'http://cloud.lab.fiware.org:4730/'
    os.environ['OS_AUTH_URL'] = 'http://cloud.lab.fiware.org:4730/v2.0'

    # load data from servers
    map = OpenStackMap('tmp_cache', auto_load=False)
    map.load_keystone()

    # Get region filters and empty filter
    regions_filters = dict()
    empty_filter = None

    for filter in map.filters.values():
        if 'region_id' in filter['filters']:
            regions_filters[filter['filters']['region_id']] = filter['id']
        elif not filter['filters']:
            empty_filter = filter['id']

    useremail = dict()
    # Get users. Genuine FIWARE Users should have cloud_project_id. Be aware that
    # there are users without this field (administrators and also other users)
    for user in map.users.values():
        if 'cloud_project_id' not in user:
            continue

        project_id = user['cloud_project_id']
        found = False

        if project_id not in map.filters_by_project:
            found = False
        else:
            for filter in map.filters_by_project[project_id]:
                if filter == regions_filters[region] or filter == empty_filter:
                    found = True
                    break

        if found:
            useremail[user.id] = user.name

    return useremail


def merge_two_dicts(A, B):
    """
    Merge two dictionaries.

    :param A: Dictionary A
    :param B: Dictionary B
    :return: The merged dictionary
    """
    result = A.copy()
    result.update(B)

    return result


def processing_request(params):
    """
    Method to process the arguments received from the CLI and obtain the users list with email.

    :param params: Arguments received from the CLI.
    :return: A dictionary with the user name, user email for all the user that would use the region.
    """
    username = params['--user']
    password = params['--pass']
    region = params['--region']

    # Get top-down approx to obtain the user list
    token = get_token(username, password)
    regionid = get_endpoint_groups_id(token, region)
    projectlist = get_project_list(token, regionid)
    userset = get_user_list(token, projectlist)
    useremail = get_email(token, userset)

    # Get botton-up approx to obtain the user list
    useremail_osclient = get_email_osclient(username=username, password=password, region=region)

    # Join the two lists
    finaluserlist = merge_two_dicts(useremail, useremail_osclient)

    return finaluserlist


if __name__ == '__main__':
    version = "Get users list of one region v{}".format(__version__)
    arguments = docopt(__doc__, version=version)

    output_file = arguments['--out']

    getusers = processing_request(arguments)

    pretty_getusers = json.dumps(getusers, indent=4, separators=(',', ': '))

    if output_file is None:
        print('\n\n')
        print(pretty_getusers)
    else:
        f = open(output_file, "a")
        f.write(pretty_getusers)
        f.close()
