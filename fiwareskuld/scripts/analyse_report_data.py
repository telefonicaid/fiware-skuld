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
import glob
import cPickle as pickle

import skuld.queries

__author__ = 'chema'


def get_users_to_delete():
    """
    Get the content of users_to_delete.txt as a list
    :return: the users to delete list.
    """
    return set(user.rstrip().split([0])
               for user in open('users_to_delete.txt'))


def get_unified_report(users_to_delete):
    """Unify all the freeresources_report_*.pickle as an unique dictionary
    The dictionary is indexed by user-id and the value is a tuple with this
    fields:
    *dictionary of the resources (vms, volumes...) before the deletion
    *dictionary of the resources (vms, volumes...) after the deletion
    *True if there are not resources pending of deletion, False otherwise

    The users_to_delete list is used to filter the results. This is useful
    when some users were removed from the list after the deletion of the
    resources.

    The code fills the field "before the deletion" with the result of
    the older report found for each user, and the fields "after the deletion"
    and the boolean with the result of the more recent report found for the
    user.

    :param users_to_delete: the list of users to delete, obtained with
        get_users_to_delete()
    :return: a dictionary indexed by user-id with a tuple of resources before,
    resources after, boolean indicating if the deletion was completed.
    """
    unified = dict()
    lpreffix = len('freeresources_report_')
    lsuffix = len('.pickle')
    names = glob.glob('freeresources_report_*.pickle')
    names.sort()
    for name in names:
        users = pickle.load(open(name, 'rb'))
        for user in users:
            if user not in users_to_delete:
                continue
            if user not in unified:
                unified[user] = users[user]
            else:
                unified[user] = (unified[user][0], users[user][1],
                                 users[user][2])
    return unified


def print_summary_report(users_to_delete, report):
    """
    Print a summary of the report. How many users are in the report in
    comparison with the ones in the file users_to_delete.txt; how many users'
    deletions are completed and how many are pending.

    It also prints a summary of the freed resources.

    :param users_to_delete: the list of users to delete, obtained with
        get_users_to_delete()
    :param report: the report obtained with get_unified_report()
    :return: nothing
    """
    yes = 0
    no = 0
    total_free = dict()

    for value in report.values():
        if value[2]:
            yes += 1
        else:
            no += 1

        resources_before = value[0]
        resources_after = value[1]
        for key in resources_before.keys():
            removed = len(resources_before[key]) - len(resources_after[key])
            if removed:
                total_free[key] = total_free.get(key, 0) + removed

    print('\n===Summary==')
    msg = 'Total deleted: {}/{} Completed: {} No completed: {}'
    msg = msg.format(len(report), len(users_to_delete), yes, no)
    print(msg)

    print('Resources freed: ' + str(total_free))


def print_fails_report(report):
    """Print the users with resources that were not deleted and those
    resources. Print also a summary of the categories (vms, volumes...) where
    there are resources not deleted.

    :param report: the report obtained with get_unified_report()
    :return: nothing
    """

    print('===Pending deletions report===')
    categories = set()
    for key in report:
        if not report[key][2]:
            after = report[key][1]
            modified = dict()
            for resource in after:
                if after[resource]:
                    modified[resource] = after[resource]
                    categories.add(resource)
            print(key, modified)

    print('Categories not completed: {}'.format(categories))


def save_failed_users_list(users_to_delete, unified):
    """Create file users_to_delete_failed.txt, with the ids of users who
    were failed. Only the users with basic type are included.

    A user is considered failed if he/she has resources
    after invoking the scripts, according to the report, or if he/she does not
    appear in the report.
    :param users_to_delete: the list of users to delete, obtained with
        get_users_to_delete()
    :param unified: the report obtained with get_unified_report()

    """
    q = skuld.queries.Queries()
    with open('users_to_delete_failed.txt', 'w') as f:
        users_deleted = set()
        users_deleted.update(unified.keys())
        failed1 = users_to_delete - users_deleted
        failed2 = set(user for user in unified if not unified[user][2])
        failed = failed1.union(failed2)
        for user in failed:
            try:
                user_type = q.get_type_fiware_user(user)
                if user_type == 'basic':
                    f.write(user + '\n')
            except Exception:
                continue

if __name__ == '__main__':
    print('getting users to delete')
    users_to_delete = get_users_to_delete()
    print('unifying reports')
    report = get_unified_report(users_to_delete)
    print('saving failed users lists')
    save_failed_users_list(users_to_delete, report)
    print('printing reports')
    print_fails_report(report)
    print_summary_report(users_to_delete, report)
