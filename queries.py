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


class Queries(object):
    def __init__(self):
        self.osclients = osclients.OpenStackClients()
        self.glance = self.osclients.get_glanceclient()
        self.nova = self.osclients.get_novaclient()

    def get_all_vms(self):
        """
        get all the vms in the region
        :return: a dict with all the VM indexed by id
        """
        return dict((v.id, v) for v in self.nova.servers.list(
            search_opts={'all_tenants': 1}))

    def get_images(self):
        """
        get all the images the tenant has access in the region
        :return: a dict of images, indexed by id
        """
        return dict((image.id, image)
                    for image in self.glance.images.list(is_public=None))

    def get_public_images(self):
        """
        get all the public images
        :return: a dict of images, indexed by id
        """
        return dict((i.id, i) for i in self.glance.images.list()
                    if i.is_public)

    def get_images_with_uses(self, only_public=True, discard_owned_vm=False):
        """
        get all the images, every one will have the list of VMs
        :return: a dict indexed by id. The dict value is a tuple: the first
        value is the image object, the second a list of vms.

        Note: if is possible that a private image is in use by another tenant,
        because it was public when the VM was created.
        """
        if only_public:
            images = dict((i.id, (i, list()))
                          for i in self.glance.images.list() if i.is_public)
        else:
            images = dict((i.id, (i, list()))
                          for i in self.glance.images.list(is_public=None))
        vms = self.get_all_vms()

        for vm in vms.values():
            image_id = vm.image['id']
            if image_id in images:
                image_owner = images[image_id][0].owner
                if not discard_owned_vm or vm.tenant_id != image_owner:
                    (i, l) = images[image_id]
                    l.append(vm)

        return images

    def get_imageset_othertenants(self, flag=None):
        """return a set with all the images ids used by a tenant different than
         the owner of the image
        :param flag: if is not None, only select the image if this property
        is in the image.
        :return: a set with the IDs of the images

        Note: there is no contradiction in only_public=False,
              discard_owned_vm=True, because the image could be public formerly
              and then became private.
        """
        images = set(image[0].id for image in self.get_images_with_uses(
                     only_public=False, discard_owned_vm=True).values()
                     if len(image[1]) > 0 and
                     (not flag or flag in image[0].properties))
        return images

    def get_vms_using_image(self, image_id, discard_owned_vm=False, flag=None):
        """
        Get a list of vms using the image
        :param image: the id of the image
        :param discard_owned_vm: ignore VM owned by the same tenant than the
        image. This is useful to detect if a shared image is in use by other
        tenants.
        :param flag: if is not None, only select the image if this property
        is in the image.
        :return: a list of vms using the image (the list may be empty)
        """
        image = self.glance.images.get(image_id)
        vms = self.get_all_vms().values()
        if discard_owned_vm:
            vms_image = list(vm for vm in vms if vm.image['id'] == image_id
                             and vm.tenant_id != image.owner and (not flag or
                             flag in image.user_properties))
        else:
            vms_image = list(vm for vm in vms if vm.image['id'] == image_id and
                             (not flag or flag in image.user_properties))

        return vms_image

    def get_orphan_images_without_use(self):
        """Return a set with ids of images with are orphan (an image is orphan
        when the user resources were deteleted, but it was preserved
        because it was in use by another tenant) and are not used by any VM"""
        images_in_use = self.get_imageset_othertenants('orphan_image')
        orphan_images = set(image.id for image in self.get_images().values()
                            if 'orphan_image' in image.properties)
        return orphan_images - images_in_use
