#!/usr/bin/env python

import time
import sys

from utils.osclients import osclients

network_names = {
   'management': 'node-int-net-01',
   'tunnel': 'tunnel-net',
   'external': 'external-net'
}

subnet = {
   'management': '192.168.192.0/18',
   'tunnel': '192.168.57.0/24',
   'external': '192.168.58.0/24'
}

public_network_name = 'node-int-net-01'
testbed_network_name = 'node-int-noinet-net-02'
flavor_name = 'm1.large'
image_name = 'keyrock-R4.4'
vm_name = 'testbedskuld'
key_name = 'createimage'
security_group = 'sshopen'
# Use this IP if it is available.
preferred_ip = None
# filename of init_script
#init_script = 'install.sh'
init_script = None
# files to inject (max 10Kb). This requires special support in the installation.
upload_files = {'/home/ubuntu/install.sh': 'install.sh'}
upload_files = None


extra_params = dict()

# Get networks

network = dict()
neutron = osclients.get_neutronclient()
testbed_network = None
for net in neutron.list_networks()['networks']:
    for n in network_names:
        if net['name'] == network_names[n]:
            network[n] = net

for n in network_names:
    if not n in  network:
        network[n] = neutron.create_network({'network': {'name':
            network_names[n], 'admin_state_up': True}})['network']
        # create subnetwork. It is not possible to assign a network
        # to a VM without a subnetwork.
        neutron.create_subnet({'subnet': {'network_id': network[n]['id'],
            'ip_version': 4, 'cidr': subnet[n] }})
        

# Get floating IP
floating_ip = None
for ip in neutron.list_floatingips()['floatingips']:
    floating_ip = ip['floating_ip_address']
    if not preferred_ip or preferred_ip == floating_ip:
        break

# Get image
glance = osclients.get_glanceclient()
image = glance.images.find(name=image_name)

# Get flavor
nova = osclients.get_novaclient()
flavor = nova.flavors.find(name=flavor_name)

# load script to launch with nova.servers.create()
if init_script:
    data = open(init_script).read()
    extra_params['userdata'] = data

# inject files
if upload_files:
    files = dict()
    for filepath in upload_files:
        h = open(upload_files[filepath])
        files[filepath] = h
    extra_params['files'] = files 

# Launch VM
nics = [{'net-id': network['management']['id']},
        {'net-id': network['tunnel']['id']},
        {'net-id': network['external']['id']}]

server = nova.servers.create(
    vm_name, flavor=flavor.id, image=image.id, key_name=key_name,
    security_groups=[security_group], nics=nics, **extra_params)

print('Created VM with UUID ' + server.id)

# wait until the vm is active
tries = 1
while server.status != 'ACTIVE' and tries <30:
    print('Waiting for ACTIVE status. (Try ' + str(tries) + '/30)')
    time.sleep(5)
    server = nova.servers.get(server.id)
    tries += 1

if server.status != 'ACTIVE':
    sys.stderr.write('Failed waiting the VM is active\n')
    sys.exit(-1)

# assign the floating ip
if floating_ip:
    print('Assigning floating IP ' + floating_ip)
    server.add_floating_ip(floating_ip)
