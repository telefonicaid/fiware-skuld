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

from queries import Queries
import cPickle as pickle

"""This scripts generate a file with a set of images ids that are in use by
at least another tenant different than the owner of the image

Invoke this script before deleting the users if you don't want to remove
the images of the tenant in use by other tenants.
"""
q = Queries()

image_set = q.get_imageset_othertenants()
print image_set
with open('imagesinuse.pickle', 'wb') as f:
    pickle.dump(image_set, f, protocol=-1)
