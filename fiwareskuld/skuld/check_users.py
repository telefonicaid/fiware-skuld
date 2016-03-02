#!/usr/bin/env python

import queries

q = queries.Queries()
from utils.osclients import osclients
from conf import settings


class CheckUsers(object):
    """This class is for checking that the users that were converted to basic
    are still basic users before deleting their resources"""

    def __init__(self):
        """constructor, build the list of basic users included in
        users_to_delete.txt"""
        basic_type = settings.BASIC_ROLE_ID
        self.ids = set(
            line.strip() for line in open('users_to_delete.txt').readlines())
        keystone = osclients.get_keystoneclientv3()
        self.users_basic = set(
            asig.user['id']
            for asig in keystone.role_assignments.list(domain='default')
            if asig.role['id'] == basic_type and asig.user['id'] in self.ids)

    def report_not_basic_users(self):
        """report if there are users to delete that are not basic now"""
        no_basic_users = self.ids - self.users_basic
        if not no_basic_users:
            print('All is OK')
        else:
            print 'Users that are not basic: ', no_basic_users
            for user in no_basic_users:
                try:
                    user_type = q.get_type_fiware_user(user)
                except Exception:
                    user_type = 'unkown'
                print(user + ' ' + user_type)

if __name__ == '__main__':
    check = CheckUsers()
    check.report_not_basic_users()
