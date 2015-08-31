==========================
delete_os_tenant_resources
==========================

Introduction
============

This code is a series of scripts to free the resources allocated by the expired
 trial users and to to change the user type from trial to ordinary.

This project is part of FIWARE_.

Components
__________

There is only one component, implemented with scritps and python classes:

osclients.py
    This class provides access to all the OpenStack clients. It may be reused
in other projects.

the *_resources.py modules
    Provide the methods to list/delete resources from this class

impersonate.py
    Provide methods to impersonate a user using trusted ids.

expired_users.py
    Obtains the list of expired trial accounts

change_password.py
    A tool to change the password of any OpenStack user

queries.py
    Some useful methods to get information from OpenStack servers

phase*.py
    The scripts that free the resources


Description
===========

The purpose of these scripts is to detected the trial accounts that are expired,
free the associated resources and change the user type from trial to ordinary.

Most of the user resources are not really associated with users but with tenants;
an exception is user keys. Therefore, the resources of the tenant associated with
the trial account must be freed. Note that if a user has worked also in other
projects (tenants), these other resources must not be deleted.

The resources that these scripts can free, fall in following categories:
* nova resources: vms, user keys, security groups (only the default security
group cannot be deleted)
* glance resources: images (snapshots are also images)
* cinder resources: volumes, snapshot-volumes, backup-volumes
* neutron resources: networks, subnets, ports, routers, floating ips, security groups.
* blueprint resources: bluepint, templates
* swift resources: containers, objects

Optionally, images created by the user but in use by other tenants, may be preserved.

The deletion of the resources follow and order, for example snapshot volumes must be removed
before volumes, or blueprint instances before templates. The code try to minimize pauses
executing firts all the deletion from the same priority for each user.

The deletion scripts has the particularity that are not invoked by the admin but
by impersonating the users themselves. This is the only way to delete the key pairs and
for other resources has the advantage that it is impossible to delete the resources of other
users because the lack of permissions.

Build and Install
=================

Requirements
------------

- This scripts has been tested on a Debian 7 system, but any other recent Linux
distribution with the software described should work

The following software must be installed (e.g. using apt-get on Debian and
Ubuntu, or with yum in CentOS):

- Python 2.7
- pip

Installation
------------

The recommend installation method is using a virtualenv. Actually, the installation
process is only about the python dependencies, because the scripts do not need
installation.

1) Create a virtualenv 'delete_ENV' invoking *virtualenv deleteENV*
2) Activate the virtualenv with *source deleteENV/bin/activate*
3) Install the requirements running *pip install -r requirements.txt --allow-all-external*

Now the system is ready to use. For future sessions, only the step2 is required.

Configuration
-------------

The only configuration file is *settings/settings.py*. The following options may
be set:
* LOGGING_PATH. Default value, /var/log/fiware-trialusermanagement, requires
permission to write on /var/log
* TRIAL_ROLE_ID. Probably this value does not have to be changed if you are using FiwareLab. It is the ID of
the trial account type.
* BASIC_ROLE_ID. Probably this value does not have to be changed if you are using FiwareLab. It is the ID of
the ordinary account type (without cloud resources access)
* KEYSTONE_ENDPOINT. The Keystone endpoint.
* HORIZON_ENDPOINT. The Horizon endpoint.
* TRUSTEE =  The account to use to impersonate the users. It MUST NOT have admin privileges.
* MAX_NUMBER_OF_DAYS = The number of day after the trial account is expired. Default is 14 days.
* DONT_DELETE_DOMAINS = A set with e-mail domains. The resources of the users with ids in these domains
must not be freed, even if the accounts are trial and expired.

The admin credential is not stored in any configuration file. Instead, the usual OpenStack environment
variables (OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_REGION_NAME) must be set.

Running
=======

The procedure works by invoking the scripts corresponding to different phases:

*phase0: phase0_generateuserlist.py. This script generate the list of expired
trial users. The output of the script is the file users_lists.txt. This script
requires the admin credential.

*phase0b: phase0b_notify_users.py. The script sends an email to each expired
user whose resources is going to be deleted (i.e. to each user listed in the
file users_list.txt). The idea is to run this script a day or two before the
following scripts, to give some time to users to react before their resources
are freed.

*phase1: alternative 1: phase1_resetpasswords.py. This script has as input the
 file users_list.txt. It sets a new random password for each user and generates
the file users_credentials.txt with the user, password and tenant for each
user. This script also requires the admin credential. The handicap of this
alternative is that if users are not deleted at the end, then they need to
 recover the password, unless a backup of the password database is restored
 manually (unfortunately this operation is not possible via API).

*phase1: alternative 2: phase1_generate_trust_ids.py. This script has as input
the file users_list.txt. It generates a trust_id for each user and generates
the file users_trusted_ids.txt. The idea is to use this token to impersonate the
user without touching their password. The disadvantage is that it requires a
change in the keystone server, to allow admin user to generate the trust_ids,
because usually only the own user to impersonate is allowed to create these
tokens. Another disadvantage is that user can login and create new resources
 until phase4 script is invoked. The generated *trust ids* by default are only
valid during one hour; after that time this script must be executed again to
generate new tokens.

*phase2: phase2_stopvms.py. This scripts does not delete anything, yet. It
stops the VMs of the users and makes private their shared images. The idea is
to grant a grace period to users to detect that their resources are not
available before they are beyond redemption. This script does not require the
admin account, because it applies the user' credential from
users_credentials.txt or the trust ids from users_trusted_ids.txt.

*phase2b: phase2b_detectimagesinuse.py. This is an optional script, to detect images
owned by the user, in use by other tenants. Theoretically deleting a image used
 by a VM doesn't break the VM, but if you prefer avoid deleting that
images, invoke this script before phase3. The script purge_images.py may be
invoked after, to delete the images with no VM anymore. This script requires
the admin credential. It generates the file imagesinuse.pickle.

*phase3: phase3_delete.py. This is the point of no return. Resources are
removed and cannot be recovered. This script does not require the admin
credential, because it applies either the user's credential from
users_credentials.txt or the trusted ids from users_trusted_ids.txt. If using
*trust ids*, the script phase1_generate_trust_ids.py must be invoked again
before this script, because the phase2 script delete the *trust id* after using
it.

*phase4: phase4_change_category.py. Change the type of user from trial to basic
This script requires the admin credential. It reads the file users_to_delete.txt.
Please, note that phase4 script must no be executed for each region,
but only once, at the end of the process.

Please, be aware that scripts phase2, phase2b and phase3 must be invoked for
each region and OS_REGION_NAME must be filled accordingly.

Scripts phase0, phase1, phase2b and phase4 requires setting OS_USERNAME,
OS_PASSWORD, OS_TENANT_NAME with the admin credential

Scripts phase2 and phase3 do not require OS_USERNAME, OS_PASSWORD nor OS_TENANT_NAME
if using the phase1 change password alternative. If using *trust_ids* only
OS_PASSWORD must be set with the password of the trustee (i.e. the account used
to impersonate the users).

The phase3_delete.py generates a pickle file (named freeresources-<datatime>.pickle)
This is a dictionary of users, each entry is a tuple with another two dictionaries:
the first references the resources before deletion and the second the resources
after deletion.

Testing
=======

Unit tests
----------

To run unit test, invoke *test_expired_users.py* inside *tests* folder

Acceptance tests
----------------

See <tests/acceptance_tests/README.md>

Tools
-----

The script *create_resources.py* may be used to create resources in a real
infrastructure. OS_USERNAME, OS_TENANT_NAME/OS_TENANT_ID/OS_TRUST_ID,
OS_PASSWORD and OS_AUTH_URL must be set accordingly. Then run:

.. code::
    export PYTHONPATH=.
    tests/create_resources.py
    tests/list_resources.py

The script *tests/list_resources.py* is useful to list the resources created
and to run again after cleaning the resources.

License
-------

\(c) 2015 Telefónica I+D, Apache License 2.0


.. REFERENCES

.. _FIWARE Lab: http://www.fiware.org/lab/

