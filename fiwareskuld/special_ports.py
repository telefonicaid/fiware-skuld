class SpecialPortRemover(object):
    """Class to delete ports associated to routers not owned by the port
    owner. To delete these ports, an admin credential is needed"""

    def __init__(self):
        """constructor"""
        self.logger = logging.getLogger(__name__)
        OpenStackMap.load_filters = False
        osmap = OpenStackMap(objects_strategy=OpenStackMap.NO_CACHE_OBJECTS,
                             auto_load=False)
        osmap.load_keystone()
        osmap.load_neutron()
        self.map = osmap
        self.neutron = self.map.osclients.get_neutronclient()

    def _get_users_to_delete(self):
        """
        Read the file with the users to delete and returns a list
        :return: a list with the ids of the users to delete
        """
        try:
            users = open('users_to_delete.txt')
        except Exception:
            self.logger.error('The users_to_notify.txt file must exists')
            sys.exit(-1)

        list_users = list()
        for line in users.readlines():
            user_id = line.strip().split(',')[0]
            if user_id == '':
                continue
            list_users.append(user_id)
        return list_users

    def _get_tenants_to_delete(self, users):
        """Returns a set with the cloud project ids of the specified users

        :param users: the users to delete
        :return: a set with the project ids of the users
        """
        users = self._get_users_to_delete()
        tenants = set(self.map.users[user].cloud_project_id for user in users)
        return tenants

    def _get_router_ports_tenants(self, tenants):
        """
        return a list with the special ports to delete
        :param tenants:
        :return: a list of port objects
        """
        ports = list()
        for port in self.map.ports.values():
            if port.tenant_id in tenants and \
                    port.device_owner.startswith('network:router_interface'):
                router = self.map.routers[port.device_id]
                if router.tenant_id != port.tenant_id:
                    ports.append(port)
        return ports

    def delete_special_ports(self):
        """
        delete the users' ports that are interfaces in routers of a
        different tenant; these ports can not be deleted without an admin
        credential.
        :return: nothing
        """
        users = self._get_users_to_delete()
        tenants = self._get_tenants_to_delete(users)
        ports = self._get_router_ports_tenants(tenants)

        deleted = 0
        count = 0
        for port in ports:
            try:
                subnet = port['fixed_ips'][0]['subnet_id']
                body = {'subnet_id': subnet}
                msg = 'Removing port {0} ({1}/{2})'
                count += 1
                self.logger.info(msg.format(port.id, count, len(ports)))
                self.neutron.remove_interface_router(
                    router=port['device_id'], body=body)
                deleted += 1
            except Exception, e:
                self.logger.error('Error deleting port' + port.id + 'Reason: ' + str(e))
        if len(ports):
            print('Deleted {0}/{1} ports'.format(deleted, len(ports)))
        else:
            print('There were not any ports to delete')
