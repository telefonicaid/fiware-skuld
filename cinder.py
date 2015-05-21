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

cinder = osclients.get_cinderclient()


def get_all_volumes():
    volumes_by_tenant = dict()
    for volume in cinder.volumes.list(search_opts={'all_tenants': 1}):
        tenant = volume.__dict__['os-vol-tenant-attr:tenant_id']
        if tenant not in volumes_by_tenant:
            volumes_by_tenant[tenant] = list()
        volumes_by_tenant[tenant].append(volume.id, volume.user_id)
    return volumes_by_tenant


def get_all_backup_volumes():
    volumes_by_tenant = dict()
    for volume in cinder.backups.list(search_opts={'all_tenants': 1}):
        tenant = volume.__dict__['os-vol-tenant-attr:tenant_id']
        if tenant not in volumes_by_tenant:
            volumes_by_tenant[tenant] = list()
        volumes_by_tenant[tenant].append(volume.id, volume.user_id)
    return volumes_by_tenant


def get_all_snapshots():
    volumes_by_tenant = dict()
    for volume in cinder.volume_snapshots.list(search_opts={'all_tenants': 1}):
        tenant = volume.__dict__['os-vol-tenant-attr:tenant_id']
        if tenant not in volumes_by_tenant:
            volumes_by_tenant[tenant] = list()
        volumes_by_tenant[tenant].append(volume.id, volume.user_id)
    return volumes_by_tenant


def get_tenant_volumes(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    volumes = list()
    for volume in cinder.volumes.list():
        volumes.append((volume.id, volume.user_id))
    return volumes


def delete_tenant_volumes(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for volume in cinder.volumes.list():
        volume.delete()


def get_tenant_backup_volumes(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    volumes = list()
    for volume in cinder.backups.list():
        volumes.append((volume.id, volume.user_id))
    return volumes


def delete_tenant_backup_volumes(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for volume in cinder.backups.list():
        volume.delete()


def get_tenant_volume_snapshots(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    snapshots = list()
    for snapshot in cinder.volume_snapshots.list():
        snapshots.append(snapshot.id)
    return snapshots


def delete_tenant_volume_snapshots(tenant_id=None):
    if not tenant_id:
        tenant_id = osclients.get_session().get_project_id()

    for snapshot in cinder.volume_snapshots.list():
        snapshot.delete()
