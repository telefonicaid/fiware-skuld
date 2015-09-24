#!/usr/bin/env python

from osclients import osclients
import queries

import sys

user=osclients.get_keystoneclientv3().users.get(sys.argv[1])
print user.to_dict()
q = queries.Queries()
print q.get_type_fiware_user(user.id)
