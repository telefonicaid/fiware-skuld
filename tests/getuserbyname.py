#!/usr/bin/env python

from osclients import osclients
import queries
import sys

q = queries.Queries()
user=osclients.get_keystoneclientv3().users.find(name=sys.argv[1])
print user.to_dict()
print q.get_type_fiware_user(user.id)
