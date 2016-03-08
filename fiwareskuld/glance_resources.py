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


# snapshots are listed as images. Don't need special treatment.

class GlanceResources(object):
    """This class represent the Glance resources of a tenant. It includes
    methods to delete and query the resources"""

    def __init__(self, osclients):
        """Constructor. It requires an OpenStackClients object

        :param osclients: an OpenStackClients method (module osclients)
        :return: nothing
        """
        self.osclients = osclients
        self.glance = osclients.get_glanceclient()
        self.tenant_id = osclients.get_session().get_project_id()

    def on_region_changed(self):
        """Method invoked when the region is changed"""
        self.glance = self.osclients.get_glanceclient()

    def get_tenant_images(self):
        """ return a list of images ids

        :return: a list of image ids
        """
        images = list()
        for image in self.glance.images.findall(owner=self.tenant_id):
            if image.owner != self.tenant_id:
                continue
            images.append(image.id)
        return images

    def get_tenant_images_tuple(self):
        """ return a tuple with two list of images: the private images and the
        shared images. It is safe to delete the private images after killing
        the VMs, but the shared images requires more attention because they
        may be in use by other tenants. Deleting an image in use theoretically
        does not affect the VM (even it is should be possible to rebuild the
        image)

        :return: a tuple with the list of private images and the public images
        """
        public_images = list()
        private_images = list()
        for image in self.glance.images.findall(owner=self.tenant_id):
            if image.owner != self.tenant_id:
                continue
            if image.is_public:
                public_images.append(image.id)
            else:
                private_images.append(image.id)

        return private_images, public_images

    def delete_tenant_images(self, also_shared=False):
        """delete all the private tenant's images. If also_shared is True,
        delete also the public images.

        :param also_shared: True to delete also the shared images
        :return:
        """
        for image in self.glance.images.findall(owner=self.tenant_id):
            if image.owner != self.tenant_id:
                continue

            if image.is_public and not also_shared:
                continue
            else:
                self.glance.images.delete(image.id)

    def delete_tenant_images_notinuse(self, images_in_use):
        """delete all the tenant images, but check that they are not in the
        set 'images_in_use'. If the image is in the set, activate flag
        'orphan_image'.
        :param images_in_use: a set of images ids that should not be deleted
                              because other tenants are using them.
        :return: nothing"""
        for image in self.glance.images.findall(owner=self.tenant_id):
            if image.owner != self.tenant_id:
                continue

            if image.id in images_in_use:
                image.properties['orphan_image'] = True
                image.update(is_public=False, properties=image.properties)
            else:
                self.glance.images.delete(image.id)

    def delete_image_list(self, images):
        """delete a list of images, provided by id.
        :param images: a list of image ids
        :return: nothing
        """
        for image in images:
            self.glance.images.delete(image.id)

    def unshare_images(self):
        """Turn to private all the public images of the tenant
        :return: nothing
        """
        for image in self.glance.images.findall(owner=self.tenant_id):
            if image.owner != self.tenant_id:
                continue
            if image.is_public:
                image.update(is_public=False)
