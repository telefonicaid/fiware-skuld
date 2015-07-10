==========================
delete_os_tenant_resources
==========================


Description
-----------

This is a script to list/delete the resources of a tenant (and also the keypairs of the user)

It uses the OpenStack Pythons API:

* python-keystoneclient
* python-novaclient
* python-glanceclient
* python-cinderclient
* python-neutronclient
* python-swiftclient

Components
----------


How to use
----------

The procedure works by invoking the scripts corresponding to different phases:

*phase0: phase0_generateuserlist.py. This scripts generate the list of expired
trial users. The output of the script is the file users_lists.txt. This script
requires the admin credential.

*phase1: phase1_resetpasswords.py. This scripts has as input the file
users_list.txt. It sets a new random password for each user and generates the file
users_credentials.txt with the user, password and tenant for each user. This
script also requires the admin credential.

*phase2: phase2_stopvms.py. This scripts does not delete anything, yet. It
stops the VMs of the users and makes private their shared images. The idea is
to grant a grace period to users to detect that their resources are not
available before they are beyond redemption. This script does not require the
admin account, because it applies the user' credential from users_credentials.txt.
It generates the file imagesinuse.pickle.

*phase2b: phase2b_detectimagesinuse.py. This is an optional script, to detect images
owned by the user, but in use by other tenants. Theoretically deleting a image
in use by a VM doesn't break the VM, but if you prefer avoid deleting that
images, invoke this script before phase3. The script purge_images.py may be
invoked after, to delete the images with no VM anymore. This script requires
the admin credential.

*phase3: phase3_delete.py. This is the point of no return. Resources are
removed and cannot be recovered. This script does not require the admin
credential, because it applies the user's credential from users_credentials.txt.

*phase4: phase4_change_category.py. Change the type of user from trial to basic
This script requires the admin credential. It reads the file users_to_delete.txt.



License
-------

\(c) 2015 Telefónica I+D, Apache License 2.0


.. REFERENCES

.. _FIWARE Lab: http://www.fiware.org/lab/

