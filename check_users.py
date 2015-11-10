#!/usr/bin/env python

import queries

q=queries.Queries()
from osclients import osclients
from settings import settings

class CheckUsers(object):
     """This class is for checking that the users that were converted to basic are
        still basic users before deleting their resources"""

     def __init__(self):
         """constructor, build the list of basic users included in users_to_delete.txt"""
         typeuser = settings.BASIC_ROLE_ID
         self.ids = set(line.strip() for line in open('users_to_delete.txt').readlines())
         k = osclients.get_keystoneclientv3()
         self.users_basic = set(
              asig.user['id'] for asig in k.role_assignments.list(domain='default')
              if asig.role['id'] == typeuser and asig.user['id'] in self.ids)

     def report_not_basic_users(self):
          """report if there are users to delete that are not basic now"""
          no_basic_users = self.ids - self.users_basic
          if not no_basic_users:
              print 'All is OK'
              return
          print 'Users that are not basic: ', no_basic_users 
          for user in no_basic_users:
              try:
                  type = q.get_type_fiware_user(user)
              except:
                  type = 'unkown'
                  print user, type

if __name__ == '__main__':
    check = CheckUsers()
    check.report_not_basic_users()
