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


class SwiftResources(object):
    """This class represent the Swift resources of a tenant. It includes
    methods to delete and query the resources"""
    def __init__(self, osclients):
        """Constructor. It requires an OpenStackClients object

        :param osclients: an OpenStackClients method (module osclients)
        :return: nothing
        """
        self.swiftclient = osclients.get_swiftclient()
        self.tenant_id = osclients.get_session().get_project_id()
        self.osclients = osclients

    def on_region_changed(self):
        """Method invoked when the region is changed"""
        self.swiftclient = self.osclients.get_swiftclient()

    def get_tenant_containers(self):
        """return all the tenant's containers
        :return: a list of containers names
        """
        account = self.swiftclient.get_account()
        return list(container['name'] for container in account[1])

    def get_tenant_containers_dicts(self):
        """return all the tenant's containers as a dict: the key is the
        container name and the value is a list with the name of its objects.
        :return:
        """
        containers_list = self.get_tenant_containers()
        containers = dict()
        for container_name in containers_list:
            container = self.swiftclient.get_container(container_name)
            objects = list(obj['name'] for obj in container[1])
            containers[container_name] = objects

    def get_tenant_objects(self):
        """ Return all the objects as tuples container,path
        :return: a tuple (container,path)
        """
        containers_list = self.get_tenant_containers()
        object_list = list()
        for container_name in containers_list:
            container = self.swiftclient.get_container(container_name)
            for obj in container[1]:
                object_list.append((container_name, obj['name']))
        return object_list

    def delete_tenant_containers(self):
        """delete all the swift contents of the tenant. That is,
        each container with theirs objects

        :return: Nothing
        """
        containers_list = self.get_tenant_containers()
        for container_name in containers_list:
            container = self.swiftclient.get_container(container_name)
            for obj in container[1]:
                self.swiftclient.delete_object(container_name, obj['name'])
            self.swiftclient.delete_container(container_name)
