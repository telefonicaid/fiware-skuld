#!/usr/bin/env python

import argparse
import osclients
import base64

def change_password(username, newpassword):
    keystone = osclients.get_keystoneclientv3()
    id = keystone.users.find(name=username).id
    (resp,user) = keystone.users.client.get('/users/' + id)
    if not resp.ok:
        raise Exception(str(resp.status_code) + ' ' + resp.reason)
    user['user']['password'] = newpassword
    (resp,user) = keystone.users.client.patch('/users/' + id, body=user)
    if not resp.ok:
        raise Exception(str(resp.status_code) + ' ' + resp.reason)

def change_identity(username, password):
    if not password:
        rand = open('/dev/urandom')
        password = base64.b64encode(rand.read(12))
        change_password(username, password)

    # Obtain project_id of user
    keystone_client = osclients.get_keystoneclient()
    user = keystone_client.users.find(name=username)
    tenant = user.cloud_project_id

    # Preserve admin session before changing to user one
    osclients.preserve_session()

    # Change to user session
    osclients.set_credential(username, password, str(tenant), False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Change a user's password")
    parser.add_argument('username')
    parser.add_argument('newpassword')
    meta = parser.parse_args()
    change_password(meta.username, meta.newpassword)

