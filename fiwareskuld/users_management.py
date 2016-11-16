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


import datetime
import pickle

from fiwareskuld.conf import settings
from fiwareskuld.utils import osclients
from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.special_ports import SpecialPortRemover
from fiwareskuld.impersonate import TrustFactory
from fiwareskuld.change_password import PasswordChanger
from fiwareskuld.user_resources import UserResources
from os import environ
from fiwareskuld.utils.queries import Queries
from fiwareskuld.utils import log

logger = log.init_logs('user_management')


class UserManager(object):
    """Class to generate users."""
    def __init__(self):
        """constructor"""
        self.clients = osclients.OpenStackClients()
        self.clients.override_endpoint(
            'identity', self.clients.region, 'admin', settings.KEYSTONE_ENDPOINT)
        self.nova_c = self.clients.get_novaclient()
        self.neutron_c = self.clients.get_neutronclient()
        self.keystone = self.clients.get_keystoneclientv3()
        self.exp = ExpiredUsers()
        self._trust_info()

    def _trust_info(self):
        """
        It obtains the trust information.
        :return:
        """
        if 'TRUSTEE_PASSWORD' in environ:
            self.trust_password = environ['TRUSTEE_PASSWORD']
        elif 'TRUSTEE_PASSWORD' in dir(settings):
            self.trust_password = settings.TRUSTEE_PASSWORD
        else:
            msg = 'TRUSTEE_PASSWORD must be defined, either in settings or environ'
            raise Exception(msg)

        if 'TRUSTEE_USER' in environ:
            self.trustee = environ['TRUSTEE_USER']
        else:
            self.trustee = settings.TRUSTEE

    def add_domain_user_role(self, user, role, domain):
        """ It adds a role to a user.
        :param user: the user
        :param role: the role to add
        :param domain: the domain
        :return: nothing
        """
        manager = self.keystone.roles
        return manager.grant(role, user=user, domain=domain)

    def update_domain_to_role(self, user, role_name, date_now=None, duration=settings.COMMUNITY_MAX_NUMBER_OF_DAYS):
        """
        It updates the domain to the role
        :param user: the user
        :param role_name: the role
        :param duration: the duration for community
        :return: nothing
        """
        role = self.keystone.roles.find(name=role_name)

        if date_now:
            date_out = str(date_now)
        else:
            date_out = str(datetime.date.today())

        if role_name == "community":
            self.keystone.users.update(user, community_started_at=date_out, community_duration=duration)
        elif role_name == "trial":
            self.keystone.users.update(user, trial_started_at=date_out)

        self.add_domain_user_role(
            user=user,
            role=role.id,
            domain='default')

    def get_user(self, user_name):
        """
        It gets the user for its name
        :param user_name: the username
        :return: the user
        """
        users = self.keystone.users.list(username=user_name)
        if users and len(users) == 1:
            return users[0]
        return None

    def create_user(self, user_name, password, role_name, date_now=None):
        """
        It creates a user.
        :param user_name: username
        :param password: password
        :param role_name: the role
        :param date_now: the date to be created
        :return: the user
        """
        users = self.get_user(user_name)
        if users:
            raise Exception(403, "User {0} already exist".format(user_name))

        user = self.register_user(user_name, password, role_name, date_now)
        return user

    def register_user(self, user_name, password, role_name, date_now=None):
        """
        It register the user in the idm.
        :param user_name: username
        :param password: password
        :param role_name: the role
        :param date_now: the date to be created
        :return: the user
        """
        self.user_name = user_name
        self.password = password
        self.role_name = role_name

        user = self.keystone.user_registration.users.register_user(
            user_name,
            domain="default",
            password=password,
            username=user_name)

        self.keystone.user_registration.users.activate_user(
            user=user.id,
            activation_key=user.activation_key)

        user = self.get_user(user_name)

        if user:
            self.update_domain_to_role(user, role_name, date_now)
            self.update_quota(user, role_name)
        return user

    def update_user(self, user, role_name, date=None):
        """
        It updates the users.
        :param user: the user
        :param date: the date
        :return: nothing
        """
        self.update_domain_to_role(user, role_name, date)
        self.update_quota(user, role_name)

    def delete_user(self, user):
        """
        It deletes the user
        :param user: the user to be deleted.
        :return: nothing
        """
        users = self.keystone.users.list(username=user.username)
        if users or len(users) > 0:
            # We delete the projects belonging to the user
            projects = self.keystone.projects.list(user=users[0])
            for project in projects:
                self.keystone.projects.delete(project)
            self.keystone.users.delete(users[0])
        else:
            raise Exception(404, "User {0} not found".format(user.username))

    def delete_user_id(self, user_id):
        """
        It delete the user by its user_id
        :param user_id: the user_id
        :return: nothing
        """
        users = self.keystone.users.list(username=user_id)
        if users or len(users) > 0:
            self.delete_user(users[0])
        else:
            raise Exception(404, "User {0} not found".format(user_id))

    def _check_user_to_be_deleted(self, user):

        resources = self.get_user_resources(user)
        if resources:
            if len(resources["vms"]) > 0:
                return False
        return True

    def update_quota(self, user, role_name):
        """ It updates the quota for the user according to role requirements.
        the user should be registrated in keystone.
        :param user: the user
        :param role: the role
        :return: nothing
        """
        kargs = self.get_nova_quota(user, role_name)
        self.nova_c.quotas.update(user.default_project_id, **kargs)
        self.nova_c.quotas.update(user.cloud_project_id, **kargs)
        self.neutron_c.update_quota(user.cloud_project_id, self.get_neutron_quota(role_name))
        self.neutron_c.update_quota(user.default_project_id, self.get_neutron_quota(role_name))

    def get_neutron_quota(self, role_name):
        """
        It gets the neutron quota parameters
        :param role_name: the user role
        :return: the quota
        """
        if role_name == 'community':
            return {"quota": {"subnet": 1, "network": 1, "floatingip": 1,
                              "security_group_rule": 20, "security_group": 20,
                              "router": 1, "port": 10}}
        elif role_name == 'trial':
            return {"quota": {"subnet": 0, "network": 0, "floatingip": 1,
                              "security_group_rule": 10, "security_group": 10,
                              "router": 0, "port": 10}}
        else:
            return {"quota": {"subnet": 0, "network": 0, "floatingip": 0,
                              "security_group_rule": 0, "security_group": 0,
                              "router": 0, "port": 0}}

    def get_nova_quota(self, user, role_name):
        """
        It gets the nova quota parameters
        :param user: the user
        :param role: the role
        :return: the quota
        """

        if role_name == 'basic':
            return {"user_id": user.id, "instances": 0, "ram": 0,
                    "cores": 0, "floating_ips": 0}
        elif role_name == "trial":
            return {"user_id": user.id, "instances": 3, "ram": 6000,
                    "cores": 5, "floating_ips": 1}
        else:
            return {"user_id": user.id, "instances": 5, "ram": 10240,
                    "cores": 10, "floating_ips": 0}

    def change_to_basic_user_keystone(self, user):
        """
        It changes the role to basic.
        :param user: the user
        :return: Nothing.
        """
        roles = self.exp.get_roles_user(user)
        if "basic" in roles:
            return
        self.update_domain_to_role(user,  "basic")
        if "trial" in roles:
            role = self.keystone.roles.find(name="trial")
        elif "community" in roles:
            role = self.keystone.roles.find(name="community")
        self.keystone.roles.revoke(role, user=user, domain="default")
        # use idm url endpoint for notified users....

    def generate_trust_id(self, user):
        """
        From a list of users to delete, generate a file with a trustid for each
        user. The user is acting as the trustor, delegating in a trustee, which
        will impersonate it to delete its resources.

        :param users_to_delete: a list of trustors.
        :return: this function does not return anything. It creates a file.
        """
        trust_factory = TrustFactory(self.clients)
        user_name = None
        trust_id = None
        user_id = None
        try:
            (user_name, trust_id, user_id) = \
                trust_factory.create_trust_admin(user, self.trustee)

        except Exception, e:
            msg = 'Failed getting trust-id from trustor {0}. Reason: {1}'
            logger.error(msg.format(user, str(e)))
            print(e)

        return (user_name, trust_id, user_id)

    def change_password(self, user):
        """
        It changes the password for the user.
        :param user: the user.
        :return: The new credentials.
        """
        user_manager = PasswordChanger()
        cred_list = user_manager.get_user_cred(user)
        return cred_list

    def get_user_resources(self, user_id):
        """
        It obtains the resources for the user.
        :param user_id: the user id.
        :return: A dict with the user resources.
        """
        user = self.get_user(user_id)
        return self.get_user_resources(user)

    def create_vm_for_user(self, user_id, vm_name, image):
        """
        It creates a VM for the user, obtaining a trust id.
        :param user_id: the user id.
        :param vm_name: the vm name
        :param image: the image
        :return: Nothing.
        """
        user = self.get_user(user_id)
        user_resources = self._get_user_resources(user)
        user_resources.nova.create_nova_vm(vm_name, image)

    def delete_vms_for_user(self, user_id):
        """
        It deletes the VM for the user, obtaining a trust id.
        :param user_id: the user id.
        :return: Nothing.
        """

        user = self.get_user(user_id)
        user_resources = self._get_user_resources(user)
        user_resources.nova.delete_tenant_vms()

    def delete_secgroups_for_user(self, user_id):
        """
        It deletes the security groups for the user, obtaining a trust id.
        :param user_id: the user id.
        :return: Nothing.
        """

        user = self.get_user(user_id)
        user_resources = self._get_user_resources(user)
        user_resources.nova.delete_tenant_security_groups()

    def create_secgroup_for_user(self, user_id, sec_name):
        """
        It creates a security groups for the user obtaining a trust id.
        :param user_id: the user id
        :param sec_name: the sec group name.
        :return: Nothing.
        """
        user = self.get_user(user_id)
        user_resources = self._get_user_resources(user)
        user_resources.nova.create_security_group(sec_name)

    def _get_user_resources(self, user):
        user_resources = None
        (user_name, trust_id, user_id) = self.generate_trust_id(user)
        if trust_id:
            try:
                user_resources = UserResources(self.trustee, self.trust_password, trust_id=trust_id)
            except:
                print "Problems with user {0}. Projects is not enabled".format(user.name)
        return user_resources

    def get_regions(self, user):
        regions_str = ""
        user_resources = self._get_user_resources(user)
        if user_resources:
            for region in user_resources.regions_available:
                regions_str = regions_str + "," + region
            return regions_str
        return None

    def get_user_resources_regions(self, user):
        """
        It obtains the resources for the user.
        :param user: the user.
        :return: A dict with the user resources.
        """
        user_resources = self._get_user_resources(user)

        region_resources = {}
        if not user_resources:
            return region_resources
        for region in user_resources.regions_available:
                user_resources.change_region(region)
                region_resources[region] = user_resources.get_resources_dict()
        return region_resources

    def get_user_resources(self, user):
        """
        It obtains the resources for the user.
        :param user: the user.
        :return: A dict with the user resources.
        """
        user_resources = self._get_user_resources(user)
        return user_resources.get_resources_dict()

    def get_image(self, user):
        user_resources = self._get_user_resources(user)
        return user_resources.glance.get_images()[0].id

    def stop_vms(self, user):
        """
        It stops the vm for the user
        :param user: the user
        :return: nothing.
        """
        user_resources = self._get_user_resources(user)
        vms = user_resources.get_vms_in_dict()
        stopped = user_resources.stop_tenant_vms()

        logger.info('Stopped {0} (total {1})'.format(stopped, len(vms)))
        logger.info('Unshare public images of user ' + user.id)
        user_resources.unshare_images()
        return vms

    def stop_vms_in_regions(self, user):
        """
        It stops the vm for the user
        :param user: the user
        :return: nothing.
        """
        user_resources = self._get_user_resources(user)

        regions = user_resources.get_regions_user()
        vms_regions = {}
        for region in regions:
            user_resources.change_region(region)
            vms = user_resources.get_vms_in_dict()
            vms_regions[region] = vms
            stopped = user_resources.stop_tenant_vms()
            logger.info('Stopped {0} (total {1}) in Region {2}'.format(stopped, len(vms), region))
            user_resources.unshare_images()
            logger.info('Unshare public images of user ' + user)
        return vms_regions

    def detect_images_in_use(self):
        """
        It detects if they are images in use.
        :return: the image set.
        """
        q = Queries()

        image_set = q.get_imageset_othertenants()
        with open('imagesinuse.pickle', 'wb') as f:
            pickle.dump(image_set, f, protocol=-1)
        return image_set

    def delete_special_ports(self):
        """
        It detects if they are special ports to be removed
        and remove them.
        :return: nothing.
        """
        remover = SpecialPortRemover()
        remover.delete_special_ports()

    def delete_resources(self, user):
        """
        It deletes resources for the user.
        :param user: the user.
        :return: nothing.
        """
        (user_name, trust_id, user_id) = self.generate_trust_id(user)
        user_resources = UserResources(self.trustee, self.trust_password, trust_id=trust_id)
        report = {}
        user_resources.imagesinuse = self.detect_images_in_use()

        logger.info('user ' + user.username + ' has id ' + user_id)
        resources_before = user_resources.get_resources_dict()

        msg = "Freeing resources priority 1 user:"
        logger.info(msg)
        user_resources.delete_tenant_resources_pri_1()

        msg = "Freeing resources priority 2 user: "
        logger.info(msg)
        user_resources.delete_tenant_resources_pri_2()

        msg = "Freeing resources priority 3 user: )"
        logger.info(msg)
        user_resources.delete_tenant_resources_pri_3()

        try:
            msg = "Retrieving after resources of user:)"
            resources_after = user_resources.get_resources_dict()
        except Exception, e:
            msg = 'Error retrieving resources after freeing of user {0} cause: {1}'
            logger.error(msg.format(str(user), str(e)))
            # At least, save the resources before
            report[str(user)] = (resources_before, resources_before, False)

    def deleting_expired_trial_users_and_resources(self):
        """
        It deletes expired trial users and its resources
        :return: nothing.
        """
        yellow_users, red_users = self.exp.get_yellow_red_trial_users()
        for user in red_users:
            self.change_to_basic_user_keystone(user)
            self.stop_vms(user)
            self.delete_resources(user)
