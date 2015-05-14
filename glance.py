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


import osclients

# instantáneas de VM se listan como imágenes, no necesitamos tratarlas de
# forma especial.

def get_all_images():
    public_images = dict()
    private_images = dict()
    glance = osclients.get_glanceclient()
    for image in glance.images.findall():
        if image.is_public:
            if image.owner not in public_images:
                public_images[image.owner] = list()
            public_images[image.owner].append(image.id)
        else:
            if image.owner not in private_images:
                private_images[image.owner] = list()
            private_images[image.owner].append(image.id)
    return (private_images, public_images)

def get_tenant_images(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    tenant = osclients.get_session().get_project_id()
    public_images = list()
    private_images = list()
    glance = osclients.get_glanceclient()
    for image in glance.images.findall(owner=tenant):
        if image.owner != tenant_id:
            continue
        if image.is_public:
            public_images.append(image.id)
        else:
            private_images.append(image.id)
    return (private_images, public_images)


def delete_tenant_images(also_shared=False, tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    tenant = osclients.get_session().get_project_id()
    glance = osclients.get_glanceclient()
    for image in glance.images.findall(owner=tenant):
        if image.owner != tenant_id:
            continue

        if image.is_public and not also_shared:
            continue
        else:
            glance.images.delete(image.id)

def delete_image_list(images):
    glance = osclients.get_glanceclient()
    for image in images:
        glance.images.delete(image.id)


