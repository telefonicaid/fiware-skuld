=============================
FIWARE Trial Users Management
=============================

.. contents:: :local:

Introduction
============



This project is a scripts sets developed to free the allocated resources by the
expired Trial Users in any FIWARE Lab node and finally change the user type
from Trial User to Basic User.

This project is part of FIWARE_.

Description
===========

The purpose of these scripts are the recovering of the trial users that are expired,
free the associated resources and change the user type from trial to basic.

Most of the user resources are not really associated with users but with tenants;
an exception is user key pairs. Therefore, the resources of the tenant associated with
the trial account must be freed. Note that if a user has worked also in other
projects (tenants), these other resources must not be deleted.

The resources that these scripts can free, fall in following categories:

- nova resources: servers, user key pairs, security groups (only the default security
  group cannot be deleted)
- glance resources: images (snapshots are also images)
- cinder resources: volumes, snapshot-volumes, backup-volumes
- neutron resources: networks, subnets, ports, routers, floating ips, security groups.
- blueprint resources: bluepint, templates
- swift resources: containers, objects

Optionally, images created by the user but in use by other tenants, may be preserved.

The deletion of the resources follow and order, for example snapshot volumes must be removed
before volumes, or blueprint instances before templates. The code try to minimize pauses
executing first all the deletion from the same priority for each user.

The deletion scripts has the particularity that are not invoked by the admin but
by impersonating the users themselves. This is the only way to delete the key pairs and
for other resources has the advantage that it is impossible to delete the resources of other
users because the lack of permissions.

Components
----------

There are not properly components in this project. The code is a series of
scripts with some code organized inside python classes:

the phase\*.py scripts
    The scripts that are invoked by the users to free the resources
the \*_resources.py modules
    Provide the methods to list/delete resources from different services (nova,
    glance, neutron, cinder...)
osclients.py
    This class provides access to all the OpenStack clients. It may be reused
    in other projects.
impersonate.py
    Provide methods to impersonate a user using trusted ids.
expired_users.py
    Obtains the list of expired trial accounts
change_password.py
    A tool to change the password of any OpenStack user
queries.py
    Some useful methods to get information from OpenStack servers

Build and Install
=================

Requirements
------------

- This scripts has been tested on a Debian 7 system, but any other recent Linux
  distribution with the software described should work

The following software must be installed (e.g. using apt-get on Debian and Ubuntu,
or with yum in CentOS):

- Python 2.7
- pip
- virtualenv

Installation
------------

The recommend installation method is using a virtualenv. Actually, the installation
process is only about the python dependencies, because the scripts do not need
installation.

1) Create a virtualenv 'deleteENV' invoking *virtualenv deleteENV*
2) Activate the virtualenv with *source deleteENV/bin/activate*
3) Install the requirements running *pip install -r requirements.txt
   --allow-all-external*

Now the system is ready to use. For future sessions, only the step2 is required.

Configuration
-------------

The only configuration file is *settings/settings.py*. The following options may
be set:

* TRUSTEE =  The account to use to impersonate the users. It MUST NOT have admin
  privileges. The value is a username (e.g. trustee@example.com)
* MAX_NUMBER_OF_DAYS = The number of day after the trial account is expired.
  Default is 14 days. It is very important that this parameter has the right
  value, otherwise accounts could be deleted prematurely.
* LOGGING_PATH. Default value, ``/var/log/fiware-trialusermanagement``, requires
  permission to write on ``/var/log``
* TRIAL_ROLE_ID. Probably this value does not have to be changed when using
  FiwareLab. It is the ID of the trial account type.
* BASIC_ROLE_ID. Probably this value does not have to be changed when using
  FiwareLab. It is the ID of the ordinary account type (without cloud resources
  access)
* KEYSTONE_ENDPOINT. The Keystone endpoint.
* HORIZON_ENDPOINT. The Horizon endpoint.
* DONT_DELETE_DOMAINS = A set with e-mail domains. The resources of the users
  with ids in these domains must not be freed, even if the accounts are trial
  and expired.

The TRUSTEE parameter has a fake value that must be changed unless you use the
method to impersonate users that implies changing the passwords. See below for
details.

The admin credential is not stored in any configuration file. Instead, the
usual OpenStack environment variables (OS_USERNAME, OS_PASSWORD,
OS_TENANT_NAME, OS_REGION_NAME) must be set. In the same way, the scripts that
expect the password of the TRUSTEE, read the OS_PASSWORD environment variable.

Running
=======

The procedure works by invoking the scripts corresponding to different phases:

-phase0: ``phase0_generateuserlist.py``. This script generate the list of expired
    trial users and the users to notify because their resources are expiring in
    the next days (7 days or less). The output of the script are the files
    ``users_to_delete.txt`` and  ``users_to_notify.txt``.
    This script requires the admin credential.

-phase0b: ``phase0b_notify_users.py``. The script sends an email to each expired
     user whose resources is going to be deleted (i.e. to each user listed in
     the file ``users_to_notify.txt``). The purpose of this scripts is to give
     some time to users to react before their resources are deleted.

-phase0c: ``phase0c_change_category.py``. Change the type of user from trial to
      basic. This script requires the admin credential. It reads the file
      ``users_to_delete.txt``. Users of type basic cannot access the cloud
      portal anymore (however, the resources created are still available).
      Please, note that this script must no be executed for each region, but
      only once.

-phase1, alternative 1: ``phase1_resetpasswords.py``. This script has as input
     the file ``users_list.txt``. It sets a new random password for each user
     and generates the file ``users_credentials.txt`` with the user, password
     and tenant for each user. This script also requires the admin credential.
     The handicap of this alternative is that if users are not deleted at the
     end, then they need to recover the password, unless a backup of the
     password database is restored manually (unfortunately this operation is
     not possible via API).

-phase1, alternative 2: ``phase1_generate_trust_ids.py``. This script has as
     input the file ``users_to_delete.txt``. It generates a trust_id for each user
     and generates the file ``users_trusted_ids.txt``. The idea is to use this
     token to impersonate the user without touching their password. The
     disadvantage is that it requires a change in the keystone server, to allow
     admin user to generate the trust_ids, because usually only the own user to
     impersonate is allowed to create these tokens. Another disadvantage is that
     users can login and create new resources until phase4 script is invoked.
     The generated *trust ids* by default are only valid during one hour; after
     that time this script must be executed again to generate new tokens.

-phase2: ``phase2_stopvms.py``. This optional script does not delete anything, yet. It
     stops the servers of the users and makes private their shared images. The idea
     is to grant a grace period to users to detect that their resources are not
     available before they are beyond redemption. This script does not require
     the admin account, because it applies the user' credential from
     ``users_credentials.txt`` or the trust ids from ``users_trusted_ids.txt``.

-phase2b: ``phase2b_detectimagesinuse.py``. This is an optional script, to
     detect images owned by the user, in use by other tenants. Theoretically
     deleting a image used  by a server doesn't break the server, but if you prefer to
     avoid deleting that images, invoke this script before phase3. The script
     purge_images.py may be invoked after, to delete the images with has no VM
     anymore. This script requires the admin credential. It generates the file
     imagesinuse.pickle.

-phase3: ``phase3_delete.py``. This is the point of no return. Resources are
     removed and cannot be recovered. This script does not require the admin
     credential, because it applies either the user's credential from
     ``users_credentials.txt`` or the trusted ids from ``users_trusted_ids.txt``.
     If using *trust ids*, the script phase1_generate_trust_ids.py must be
     invoked again before this script, because the phase2 script delete the
     *trust id* after using it.


It is very important to note that phase2 and phase3 use the output of previous
phases scripts without checking again if the user is still a trial user. Therefore
if the scripts are not executed in the same day, it is convenience to recheck
if some users has been upgraded.

The following python fragment can be used to check (after the users has been
downgraded to basic) that they are still basic:

.. code::

    from osclients import osclients
    from settings import settings

    typeuser = settings.BASIC_ROLE_ID
    ids = set(line.strip() for line in open('users_to_delete.txt').readlines())
    k = osclients.get_keystoneclientv3()
    users_basic = set(
        asig.user['id'] for asig in k.role_assignments.list(domain='default')
        if asig.role['id'] == typeuser and asig.user['id'] in ids)
    print 'Users that are not basic: ',  ids - users_basic

Please, be aware that scripts phase2, phase2b and phase3 must be invoked for
each region and OS_REGION_NAME must be filled accordingly.

Scripts phase0, phase1, phase2b and require setting OS_USERNAME,
OS_PASSWORD, OS_TENANT_NAME with the admin credential

Scripts phase2 and phase3 do not require OS_USERNAME, OS_PASSWORD nor
OS_TENANT_NAME when using the phase1 change password alternative. If using
*trust_ids* only OS_PASSWORD must be set with the password of the trustee (i.e.
the account used to impersonate the users).

The phase3_delete.py generates a pickle file (named
freeresources-<datatime>.pickle). This is a dictionary of users, each entry is
a tuple with another two dictionaries: the first references the resources
before deletion and the second the resources after deletion. The tuple has a
boolean as a third value: it is True when all the users resources are deleted.

Testing
=======

Unit tests
----------

To run unit test, invoke *nosetest test_expired_users.py* inside *tests* folder

Acceptance tests
----------------

The acceptante tests are inside the folder *tests/acceptance_tests*

Prerequisites
*************

- Python 2.7 or newer
- pip installed (http://docs.python-guide.org/en/latest/starting/install/linux/)
- virtualenv installed (pip install virtalenv)
- Git installed (yum install git-core / apt-get install git)

Environment preparation
***********************
- Create a virtual environment somewhere, e.g. in ENV (virtualenv ENV)
- Activate the virtual environment (source ENV/bin/activate)
- Change to the test/acceptance folder of the project
- Install the requirements for the acceptance tests in the virtual environment
  (pip install -r requirements.txt --allow-all-external).
- Configure file in tests/acceptance_tests/commons/configuration.py adding the
  keystone url, and a valid, user, password and tenant ID.

Tests execution
***************

1) Change to the tests/acceptance_tests folder of the project if not already on it
2) Assign the PYTHONPATH environment variable executing "export PYTHONPATH=../.."
3) Run lettuce_tools with appropriate params (see available ones with the -h option)

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
and to compare the resources before and after running the scripts. Another
advantage is that the script support OS_TRUST_ID, while other tools as nova
does not.

Deletion of Unaccepted Terms & Conditions users
===============================================

You can find here details about `Deletion of users that does not accept new Terms and Conditions <scripts/unacceptedTermsAndConditions/README.rst>`_

License
=======

\(c) 2015 Telefónica I+D, Apache License 2.0


.. REFERENCES

.. _FIWARE: http://www.fiware.org/
