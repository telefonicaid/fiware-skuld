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
__author__ = 'chema'

import logging

from skuld.queries import Queries
from utils import osclients

"""This scripts delete images with the metadata 'orphan_image' when there are
no more VMs using it. It may be invoked by a cron script.

An 'orphan image' is an image that was preserved when the other resources of
the user was deleted, because it was in use by VMs of other tenants."""
q = Queries()
images = q.get_orphan_images_without_use()
if images:
    glance = osclients.OpenStackClients().get_glanceclient()
    for image in images:
        logging.info('Deleting image ' + image)
        glance.images.delete(image)
