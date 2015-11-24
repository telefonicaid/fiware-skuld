# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
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

__author__ = 'gjp'

from os import environ
from unittest import TestCase
from skuld.openstackmap import OpenStackMap
from mock import patch, MagicMock
from collections import defaultdict
import os
from requests import Response


class MySessionMock(MagicMock):
    # Mock of a keystone Session

    def get_endpoint(self, auth, **kwargs):

        if kwargs.get("service_type") == "volume":
            return "http://cloud.host.fi-ware.org:4731/v2.0"

    def get_access(self, session):

        service2 = {u'endpoints': [{u'url': u'http://83.26.10.2:4730/v3/',
                                    u'interface': u'public', u'region': u'Spain2',
                                    u'id': u'00000000000000000000000000000002'},
                                   {u'url': u'http://172.0.0.1:4731/v3/', u'interface': u'administator',
                                    u'region': u'Spain2', u'id': u'00000000000000000000000000000001'}],
                                    u'type': u'identity', u'id': u'00000000000000000000000000000045'}

        d = defaultdict(list)
        d['catalog'].append(service2)

        return d

    def request(self, url, method, **kwargs):

        resp = Response()

        if url == '/servers/detail?all_tenants=1':
            text = '{"servers": [{"status": "ACTIVE", "updated": "2015-11-23T08:08:58Z", ' \
                 '"hostId": "000000000000000123456789abcdef4fdde65ad633c1589e98a4d408", ' \
                 '"OS-EXT-SRV-ATTR:host": "host01", "addresses": ' \
                 '{"node-int-net-01": [{"OS-EXT-IPS-MAC:mac_addr": "fa:01:01:01:1a:e1", "version": 4, ' \
                 '"addr": "192.168.1.33", "OS-EXT-IPS:type": "fixed"}, {"OS-EXT-IPS-MAC:mac_addr":' \
                 ' "fa:01:01:01:1a:e1",' \
                 ' "version": 4, "addr": "83.32.33.1", "OS-EXT-IPS:type": "floating"}]},' \
                 ' "links": [{' \
                 '"href": "http://83.32.33.1:8774/v2/00000000000000000000000000000001' \
                 '/servers/00000000-0001-1c9a-v77t-1234567abcdf", "rel": "self"}, ' \
                 '{"href": "http://83.32.33.1:8774/00000000000000000000000000000001/' \
                 'servers/00000000-0001-1c9a-v77t-1234567abcdf", "rel": "bookmark"}],' \
                 ' "key_name": "keyname", "image": {"id": "00000000-0000-0000-0000-11111191712c",' \
                 ' "links": [{"href": "http://83.32.33.1:8774/00000000000000000000000000000001' \
                 '/images/00000000-0000-0000-0000-11111191712c", "rel": "bookmark"}]},' \
                 ' "OS-EXT-STS:task_state": null, "OS-EXT-STS:vm_state": "active",' \
                 ' "OS-EXT-SRV-ATTR:instance_name": "instance-00000001",' \
                 ' "OS-SRV-USG:launched_at": "2015-11-23T08:08:58.000000",' \
                 ' "OS-EXT-SRV-ATTR:hypervisor_hostname": "hostId", ' \
                 '"flavor": {"id": "4", ' \
                 '"links": [{"href": "http://83.32.33.1:8774/00000000000000000000000000000001/flavors/4", ' \
                 '"rel": "bookmark"}]}, "id": "00000000-0001-1c9a-v77t-1234567abcdf",' \
                 ' "security_groups": [{"name": "default"}], "OS-SRV-USG:terminated_at": null, ' \
                 '"OS-EXT-AZ:availability_zone": "nova", "user_id": "user", "name": "Main", ' \
                 '"created": "2015-11-23T08:08:49Z", "tenant_id": "00000000000000000000000000000001",' \
                 ' "OS-DCF:diskConfig": "MANUAL", "os-extended-volumes:volumes_attached": [], "accessIPv4": "",' \
                 ' "accessIPv6": "", "progress": 0, "OS-EXT-STS:power_state": 1, "config_drive": "",' \
                 ' "metadata": {"region": "Spain2"}}]}'

            resp.status_code = 200
            resp._content = text

        elif url == '/volumes/detail?all_tenants=1':
            text = '{"volumes": [{"status": "in-use", "display_name": "datos", "attachments":' \
                   ' [{"server_id": "123a0a4c-226d-4a93-889f-8fd3bff92002", "attachment_id":' \
                   ' "7469446f-0f25-4ad4-82f3-42e1eae01ec2", "host_name": null, "volume_id":' \
                   ' "4b5126a9-034e-4036-a347-e12a056b452c", "device": "/dev/vdc", "id":' \
                   ' "4b5126a9-034e-4036-a347-e12a056b452c"}], "availability_zone": "nova", ' \
                   '"bootable": "false", "encrypted": false, "created_at": "2015-11-21T12:13:49.000000", ' \
                   '"multiattach": "false", "os-vol-tenant-attr:tenant_id": "00000000000000000000000000000001", ' \
                   '"os-volume-replication:driver_data": null, "display_description": "datos", ' \
                   '"os-volume-replication:extended_status": null,' \
                   ' "os-vol-host-attr:host": "host01#Generic_NFS",' \
                   ' "volume_type": null, "snapshot_id": null, "source_volid": null, ' \
                   '"os-vol-mig-status-attr:name_id": null, "metadata": {"readonly": "False", "attached_mode": "rw"},' \
                   ' "id": "00000000-0341-4036-i347-e125056b452c", "os-vol-mig-status-attr:migstat": null,' \
                   ' "size": 20}]}'
            resp._content = text
            resp.status_code = 200

        elif url == '/snapshots/detail?all_tenants=1':
            text = '{"snapshots": [{"status": "error", "display_name": "testVV", "created_at": ' \
                   '"2015-08-26T10:47:48.000000", "display_description": "",' \
                   ' "os-extended-snapshot-attributes:progress": "0%", "volume_id":' \
                   ' "8eca285e-cab9-47b8-8a92-379cff8825cc", "os-extended-snapshot-attributes:project_id": ' \
                   '"00000000000000000000000000000001", "metadata": {}, "id": "00000000-5bce-410f-a953-ec09c89ed58e",' \
                   ' "size": 1}, {"status": "error", "display_name": null, "created_at": ' \
                   '"2015-09-24T06:46:17.000000", "display_description": null,' \
                   ' "os-extended-snapshot-attributes:progress": "0%", "volume_id": ' \
                   '"5bc15d1f-6b9a-1234-8000-0eba8888806", "os-extended-snapshot-attributes:project_id":' \
                   ' "ab76543d81312345bd6297a02584cbcc", "metadata": {}, "id": ' \
                   '"86034934-aec3-41b2-9b31-5f4b5a7e9c7b",' \
                   ' "size": 1}]}'
            resp._content = text
            resp.status_code = 200

        elif url == '/backups/detail':
            text = '{"backups": []}'
            resp._content = text
            resp.status_code = 200

        elif url == '/roles':
            text = '{"links": {"self": "http://cloud.host.fi-ware.org:4731/v3/roles", "previous": null, ' \
                   '"next": null},' \
                   ' "roles": [{"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789a", "links": ' \
                   '{"self": "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789a"}, ' \
                   '"name": "basic"}, {"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789b", "links": ' \
                   '{"self": "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789b"}, ' \
                   '"name": "community"}, {"id": "0bcb7fa6e85046cb9e89de123456789c", "links": {"self": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789c"}, "name":' \
                   ' "member"}, {"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789d", "links": ' \
                   '{"self": "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789d"}, ' \
                   '"name": "trial"}, {"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789e", "links":' \
                   ' {"self": "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789e"},' \
                   ' "name": "heat_stack_owner"}, {"id": "0bcb7fa6e85046cb9e89de123456789f", "links": {"self": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789f"}, "name":' \
                   ' "owner"}, {"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789g", "links": {"self":' \
                   ' "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789g"}, "name":' \
                   ' "service"}, {"is_default": true, "id": "0bcb7fa6e85046cb9e89de123456789h", "links": {"self":' \
                   ' "http://cloud.host.fi-ware.org:4731/v3/roles/0bcb7fa6e85046cb9e89de123456789h"},' \
                   ' "name": "admin"}]}'
            resp._content = text
            resp.status_code = 200

        elif url == '/users':
            text = '{"users": [{"username": "user", "name": "user", "links": {"self": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/users/00000000000000000000000000000001"}, ' \
                   '"enabled": true, "domain_id": "default", "default_project_id":' \
                   ' "00000000000000000000000000000001", "cloud_project_id": "00000000000000000000000000000001", ' \
                   '"id": "00000000000000000000000000000001"}], "links": {"self": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/users", "previous": null, "next": null}}'
            resp._content = text
            resp.status_code = 200

        elif url == '/projects':
            text = '{"links": {"self": "http://cloud.host.fi-ware.org:4731/v3/projects", "previous": null, ' \
                   '"next": null}, "projects": [{"is_cloud_project": true, "description": ' \
                   '"This organization is intended to be used in the cloud environment. As long as you are a trial' \
                   ' or community user this organization will be authorized as purchaser in the Cloud Application.",' \
                   ' "links": {"self": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/projects/00000000000000000000000000000001"}, "enabled":' \
                   ' true, "id": "00000000000000000000000000000001", "domain_id": "default", "name": "user cloud"}]}'
            resp._content = text
            resp.status_code = 200

        elif url == '/role_assignments':
            text = '{"role_assignments": [{"scope": {"project": {"id": "00000000000000000000000000000001"}},' \
                   ' "role": {"id": "00000000000000000000000000000001"}, "user": {"id":' \
                   ' "00000000000000000000000000000001"}, "links": {"assignment": ' \
                   '"http://cloud.host.fi-ware.org:4731/v3/projects/00000000000000000000000000000001' \
                   '/users/00000000000000000000000000000001"}}]}'
            resp._content = text
            resp.status_code = 200

        return resp


class TestOpenstackMap(TestCase):

    mock_session = MySessionMock()

    def setUp(self):
        self.OS_AUTH_URL = 'http://cloud.host.fi-ware.org:4731/v2.0'
        self.OS_USERNAME = 'user'
        self.OS_PASSWORD = 'password'
        self.OS_TENANT_NAME = 'user cloud'
        self.OS_TENANT_ID = '00000000000000000000000000000001'
        self.OS_REGION_NAME = 'Spain2'
        self.OS_TRUST_ID = ''
        self.OS_KEYSTONE_ADMIN_ENDPOINT = 'http://cloud.lab.fiware.org:4730'

        environ.setdefault('OS_AUTH_URL', self.OS_AUTH_URL)
        environ.setdefault('OS_USERNAME', self.OS_USERNAME)
        environ.setdefault('OS_PASSWORD', self.OS_PASSWORD)
        environ.setdefault('OS_TENANT_NAME', self.OS_TENANT_NAME)
        environ.setdefault('OS_TENANT_ID', self.OS_TENANT_ID)
        environ.setdefault('OS_REGION_NAME', self.OS_REGION_NAME)
        environ.setdefault('OS_TRUST_ID', self.OS_TRUST_ID)

    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_implement_openstackmap(self, mock_exists, mock_os):
        """test_implement_openstackmap check that we could build an empty map from the resources (VMs, networks, images,
        volumes, users, tenants, roles...) in an OpenStack infrastructure."""
        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(region=self.OS_REGION_NAME, auto_load=False)
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)

    def test_implement_openstackmap_without_region_name(self):
        """test_implement_openstackmap_without_region_name check that we could not build an empty map without providing
        a region Name."""

        del os.environ['OS_REGION_NAME']
        try:
            myopenstackmap = OpenStackMap(auth_url=self.OS_AUTH_URL, auto_load=False)
        except Exception as ex:
            self.assertRaises(ex)

    @patch('utils.osclients.session', mock_session)
    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_implement_openstackmap_with_keystone_admin_endpoint(self, mock_exists, mock_os):
        """test_implement_openstackmap_with_keystone_admin_endpoint check that we could build an empty map from the
         resources providing a keystone admin endpoint environment variable."""

        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(auto_load=False)
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)
        del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    @patch('utils.osclients.session', mock_session)
    @patch.object(os, 'mkdir')
    @patch.object(os.path, 'exists')
    def test_load_nova(self, mock_exists, mock_os):
        """test_load_nova check that we could build an empty map from nova resources."""

        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        mock_exists.return_value = False
        mock_os.return_value = True
        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.NO_CACHE_OBJECTS)

        openstackmap.load_nova()
        self.assertTrue(mock_os.called)
        self.assertIsNotNone(openstackmap)
        del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    @patch('utils.osclients.session', mock_session)
    def test_load_nova2(self):
        """test_load_nova check that we could build a map from nova resources using Direct_objects directive."""

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_nova()
        self.assertIsNotNone(openstackmap)

    @patch('utils.osclients.session', mock_session)
    def test_load_cinder(self):
        """test_load_cinder check that we could build a map from cinder resources using Direct_objects directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_cinder()
        self.assertIsNotNone(openstackmap)
        del os.environ['KEYSTONE_ADMIN_ENDPOINT']

    @patch('utils.osclients.session', mock_session)
    def test_load_keystone(self):
        """test_load_keystone check that we could build a map from keystone resources using Direct_objects directive."""
        environ.setdefault('KEYSTONE_ADMIN_ENDPOINT', self.OS_AUTH_URL)

        openstackmap = OpenStackMap(auto_load=False, objects_strategy=OpenStackMap.DIRECT_OBJECTS)
        openstackmap.load_keystone()
        self.assertIsNotNone(openstackmap)
        del os.environ['KEYSTONE_ADMIN_ENDPOINT']
