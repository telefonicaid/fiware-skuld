.. _Top:

=============================
FIWARE Trial Users Management
=============================

| |License Badge| |StackOverflow| |Build Status| |Coveralls|

.. contents:: :local:

Introduction
============

This project is a scripts sets developed to free the allocated resources by the
expired Trial Users in any FIWARE Lab node and finally change the user type
from Trial User to Basic User.

However, since a migration to a standard Horizon and a standard Keystone was made in order
to replace Keyrock and the FIWARE Cloud Portal, there's no sense in talking about Basic
user in FIWARE Cloud. Thus, some of these scripts doesn't work anymore with the new version
of FIWARE Skuld


This project is part of FIWARE_.

Top_


Description
===========

The purpose of these scripts were recovering of the trial users that are expired,
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

The deletion of the resources follow an order, for example snapshot volumes must be removed
before volumes, or blueprint instances before templates. The code try to minimize pauses
executing first all the deletion from the same priority for each user.

The deletion scripts has the particularity that are not invoked by the admin but
by impersonating the users themselves. This is the only way to delete the key pairs and
for other resources has the advantage that it is impossible to delete the resources of other
users because the lack of permissions.

The scripts can only be invoked manually

The manual way
--------------

Using the manual method implies running several scripts in a determined order.
It is the choice of the administrator who invokes the scripts when users are
notified, their VM stopped, the user type changed and the resources freed. It
is also their responsibility to recheck which users status has been changed
during the process (i.e. converted to community or amplified the trial period)
and therefore must not be deleted.


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

Top_


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

Now the system is ready to be used. For future sessions, only the step2 is required.


Configuration
-------------

The only configuration file, for most scripts is *settings/settings.py*. However, SkuldForAll_ also needs
to be configured.

The following options may be set in *settings/settings.py*:

* TRUSTEE =  The account to use to impersonate the users. It MUST NOT have admin
  privileges. The value is a username (e.g. trustee@example.com). If
  TRUSTEE_USER environment variable exits, it replaces this parameter.
* TRUSTEE_PASSWORD = The password of the account use to impersonate the users.
  This parameter may be omitted: if TRUSTEE_PASSWORD environment variable
  exits, it replaces this parameter.
* LOGGING_PATH. Default value, ``/var/log/fiware-skuld``, requires
  permission to write on ``/var/log``
* KEYSTONE_ENDPOINT. The Keystone endpoint.
* HORIZON_ENDPOINT. The Horizon endpoint.
* DONT_DELETE_DOMAINS = A set with e-mail domains. The resources of the users
  with ids in these domains must not be freed, even if the accounts are trial
  and expired.
* TRIAL_MAX_NUMBER_OF_DAYS = The number of day after the trial account is expired.
  Default is 14 days. It is very important that this parameter has the right
  value, otherwise accounts could be deleted prematurely.
* COMMUNITY_MAX_NUMBER_OF_DAYS = The number of day after the community account is expired.
  Default is 100 days. It is very important that this parameter has the right
  value, otherwise accounts could be deleted prematurely.
* NOTIFY_BEFORE_TRIAL_EXPIRED = The number of day to notify the trial users that he/she
  is going to be expired.  Default is 7 days.
* NOTIFY_BEFORE_COMMUNITY_EXPIRED = The number of day to notify the community users that he/she
  is going to be expired.  Default is 30 days.



The TRUSTEE parameter has a fake value that must be changed unless you use the
method to impersonate users that implies changing the passwords. See below for
details.

The admin credential is not stored in any configuration file. Instead, the
usual OpenStack environment variables (OS_USERNAME, OS_PASSWORD,
OS_TENANT_NAME, OS_REGION_NAME) must be set. In the same way, the scripts that
expect the password of the TRUSTEE, can use the environment variables
TRUSTEE_USER and TRUSTEE_PASSWORD, but it is also possible to use the settings
file.

Top_


Running
=======

The manual way
--------------

The recommended way of running the scripts is using the cron script. But if
user need full control, here is a description of the process.

The procedure works by invoking the scripts corresponding to different phases:

Phase0
******

This phase is there to get the users to be notified and deleted. There were a few scripts
here which did the work, whoever, since the changes in old versions, these scripts does not
work anymore. An older version of is needed.

The scripts in this phase stopped working when the new Keystone was installed replacing Keyrock. So, a set of new scripts in SkuldForAll_ has been added in order to replace the old ones.

Basially, the way to use these scripts is:

* Configuring the file ``fiware-users.ini``
* Using the scripts the following way:

To get the information out of Openstack about the users and resources:

.. code:: bash

    ./interesting_info.py > /tmp/all.json

To get the info prepared in a better way:

.. code:: bash

    ./get_outdate_people.py json > /tmp/outdated_people.json

To decide what can be deleted or not:

.. code:: bash

    ./skulded.py > /tmp/skulded.json

This last script takes into account a ``whitelist.txt`` file. It will perform a match between 
the information in ``outdated_people.json`` and its content so, the users/domains that matches
are not marked to be deleted.

To get the information in a convenient way for the scripts in phase1 and phase3, text files 
must be extracted out of these json files. **jq** is the perfect tool to do this:

- **Select Trial users to be removed**

.. code:: bash

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Trial" and .enabled==true) | .name' /tmp/skulded.json | sort > sorted_trial_users.txt

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Trial") | .id + "," + .name' ./skulded.json > users_to_delete_phase3.txt


- **Select Community users to be removed**

.. code:: bash

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Community" and .enabled==true) | .name' /tmp/skulded.json| sort > sorted_community_users.txt


    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Community") | .id + "," + .name' ./skulded.json > users_to_delete_phase3.txt


Phase1
******

* ``phase1_generate_trust_ids_new.sh``: This new script is is based on the output of the files 
  ``sorted_trial_users.txt`` and the output of ``users_to_delete_phase3.txt``. In order to 
  work this script need ssh access to the VM where Keystone is installed so it can remotely 
  invoke the script impersonate.sh_
  
  The impersonte.sh_ script updates the Keystone database to get Trustees for the one 
  Trustee user on behalf of the user who is going to be removed.
  
  The tipical use of this Script is this way:

.. code:: bash
 
 # For Trial users.
 phase1_generate_trust_ids_new.sh sorted_trial_users.txt > users_trusted_ids.txt

.. code:: bash
 
 # For Community users.
 phase1_generate_trust_ids_new.sh sorted_trial_users.txt > users_trusted_ids.txt


Phase2
******

* ``phase2_stopvms.py``. This optional script does not delete anything, yet. It
     stops the servers of the users and makes private their shared images. The idea
     is to grant a grace period to users to detect that their resources are not
     available before they are beyond redemption. This script does not require
     the admin account, because it applies the user' credential from
     ``users_credentials.txt`` or the trust ids from ``users_trusted_ids.txt``.
     If users trusted_ids, TRUSTEE_PASSWORD environment variable must be
     defined.

* phase2b: ``phase2b_detectimagesinuse.py``. This is an optional script, to
     detect images owned by the user, in use by other tenants. Theoretically
     deleting a image used  by a server doesn't break the server, but if you prefer to
     avoid deleting that images, invoke this script before phase3. The script
     purge_images.py may be invoked after, to delete the images with has no VM
     anymore. This script requires the admin credential. It generates the file
     imagesinuse.pickle.

* phase2c: ``phase2c_deletespecialports.py``. This script can be needed if
     a user subnet was added to the router of other tenant by an administrator
     (e.g. to connect to a external network). In this case, a port is created
     that only can be deleted removing the interface by an administrator.
     Therefore, this script is invoked by an administrator and deletes ports
     than the phase3 script will not be able to delete because the phase3 script
     do not use admin credentials.

After phase2, it can be usefull to remove the assignment for the user to a region, so they 
can't restart the VMs. This is done with NewFiwareKeystone_ scripts:

.. code:: bash

   user_delete_region.sh <user_mail> <region>


Phase3
******

It is recommended to wait for some days before definetely remove the user resources.

If in phase 2 the assignments of the user to the region has been done, then we might need
to re-assign the users to the region in order to be able to do the definitive deletion of
resources. The user must be reenabled and re-assigned the region using openstack CLI and 
NewFiwareKeystone_ scripts:


.. code:: bash

   openstack user set --enable <user_mail>
   user_add_region.sh <user_mail> <region>


- phase3: ``phase3_delete.py``. This is the point of no return. Resources are
     removed and cannot be recovered. This script does not require the admin
     credential, because it applies either the user's credential from
     ``users_credentials.txt`` or the trusted ids from ``users_trusted_ids.txt``.
     If using *trust ids*, the script phase1_generate_trust_ids.py must be
     invoked again before this script, because the phase2 script delete the
     *trust id* after using it. In addition, TRUSTEE_PASSWORD environment
     variable must be defined.


It is very important to note that phase2 and phase3 use the output of previous
phases scripts without checking again if the user is still a basic user. Therefore
if the scripts are not executed in the same day, it is convenience to recheck
if some users has been upgraded.

For example, in the meantime between user notification and running phase0c,
phase0 should be invoked again and use only the intersection between the old
file and the new file: the users included only in the new file are not notified
yet and the users only in the old file are probably promoted to community users
or his trial period has been extended.

The following python fragment can be used to check that users to delete
are still basic. It is useful when there is a time between running phase2 and
phase3:

.. code::

    from osclients import osclients
    from conf import settings

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

Scripts phase2 and phase3 do not require OS_USERNAME, OS_PASSWORD, etc. If using
*trust_ids*  TRUSTEE_PASSWORD must be defined either in the environment or in the
settings file. The trustee is the account used to impersonate the users.

The phase3_delete.py generates a pickle file (named
freeresources-<datatime>.pickle). This is a dictionary of users, each entry is
a tuple with another two dictionaries: the first references the resources
before deletion and the second the resources after deletion. The tuple has a
boolean as a third value: it is True when all the users resources are deleted.
A tool is provided to extract a report from free_resources-*.pickle:
*analyse_report_data.py*

Top_

The classify_resources_by_owner script
--------------------------------------

A script is provided to analyse the cloud resources on each region
and who owns them. Its main purpose is to detect anomalies,
cloud resources that are not owned by the users who can create resources:
community users, trial users and admins.

The script at first prints a summary with the number of users of each type: community,
trial and admin users can have resources. Basic users can log in the portal
but can not create cloud resources. The 'other type users' are other
users created with OpenStack tools that are not members of FIWARE. The
'users without type' are users without a role in the system. The report about
users with a project-id that does not exist, refers to a cloud-project-id
that should have all users but admins.

The script also print a summary of a set of resources in the specified regions.
The following resources are supported:

- vms: Virtual machines.
- floatingips: Floating IPs.
- networks: Networks.
- subnets: Subnetworks (i.e. IP nets).
- routers: routers to connect subnets.
- security_groups: security groups to allow/deny network traffic.
- ports: ports are created for each interface of a VM, routers, etc.
- images: glance images. Snapshots are also images.
- volumes: cinder volumes.
- volume_backups: backups of cinder volumes.
- volume_snapshot: snapshot of a volume.

For example, to print information about vms and images on Spain2 and Mexico,
run:

.. code::

    ./scripts/classify_resources_by_owners.py vms images --regions Spain2 Mexico --cache_dir ~/.cachedir

The *--cache-dir* option is to provide the directory where the information is
cached. By default this path is *~/openstackmap*. To get updated data, this
directory should be deleted or empty.

The report print the number of resources of that type:

* total. The total sum of the following four groups.
* resources owned by users community/trial/admin. This is the right situation.
* resources owned by other registered users (basic, other type, without a role).
* resources whose project-id is not the cloud-project-id of any user, but is
  an existing project-id. A specific case are the resource whose project-id is the
  default-project-id of the user intead of their cloud-project-id.
* all the other resources, that is, resources with a project-id that is not the
  cloud-project-id nor default-project-id of any user and in addition is not a
  registered project-id. This situation happens when a project has been deleted.

Top_


Testing
=======

Unit tests
----------

To run the unit tests, you need to create a virtualenv using the requirements
both contained in requirements.txt and test-requirements.txt. You only need to
execute the nosetests program in the root directory of the fiware-skuld
code. Keep in mind that it requires python2.7 to execute the unit tests.

.. code::

     virtualenv -p <root to python v2.7> venv
     source ./venv/bin/activate
     pip install -r requirements.txt
     pip install -r test-requirements.txt
     nosetests --with-coverage --cover-package=./ --exe

Unit tests with Docker execution
********************************
Skuld unit tests can be executed by docker. To do that, firstly it is required the creation of
the docker image, with the following command:

.. code::

    docker build -t fiware-skuld-build -f docker/Dockerfile_build docker

Once the fiware-skuld-build image is created, we can run it by:

.. code::

    docker run --name fiware-skuld-build fiware-skuld-build

Finally, it is possible to obtain tests results and coverage information by:

.. code::

    docker cp fiware-skuld-build:/opt/fiware-skuld/test_results .
    docker cp fiware-skuld-build:/opt/fiware-skuld/coverage .

Acceptance tests
----------------

The acceptance tests are inside the folder *tests/acceptance_tests*

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
- It is possible to deploy a valid Openstack testbed by using the fiware-testbed-deploy component: https://github.com/telefonicaid/fiware-testbed-deploy/

Tests execution
***************

1) Change to the tests/acceptance folder of the project if not already on it
2) Assign the PYTHONPATH environment variable executing "export PYTHONPATH=../.."
3) Run behave features/ --tags ~@skip --junit --junit-directory testreport.

Tools
-----

The script *tests/acceptance/commons/create_resources.py* may be used to create
resources in a real infrastructure. OS_USERNAME, OS_TENANT_NAME/OS_TENANT_ID/OS_TRUST_ID,
OS_PASSWORD and OS_AUTH_URL must be set accordingly. Then run:

.. code::

    export PYTHONPATH=.
    tests/acceptance/commons/create_resources.py
    utils/list_resources.py

The script *utils/list_resources.py* is useful to list the resources
created and to compare the resources before and after running the scripts. Another
advantage is that the script support OS_TRUST_ID, while other tools as nova does not.

Top_

Acceptance tests with Docker execution
**************************************
Skuld acceptance tests can be executed by Docker. To do that, firstly it is required the creation of
the docker image.
To do that:

.. code::

    docker build -t fiware-skuld -f docker/Dockerfile docker

Once the fiware-skuld image is created, we can run it by using docker-compose (exporting the right
environment variables).

.. code::

    export OS_AUTH_URL = {the auth uri of the testbed agains the tests are going to be execute}
    export OS_USERNAME = {the user name}
    export OS_TENANT_NAME = {the tenant name}
    export OS_PASSWORD = {the password}
    export OS_REGION_NAME = {the region}
    export OS_PROJECT_DOMAIN_NAME = {the project domain name}
    export OS_USER_DOMAIN_NAME = {the user domain name}
    docker-compose -f docker/docker-compose.yml up

When docker has finished, you can obtain the tests results by
.. code::

   docker cp docker_fiwareskuld_1:/opt/fiware-skuld/tests/acceptance/testreport .

All the scripts and docker files for the deployment of Openstack testsbed have been moved to
to fiware-testbed-deploy component: https://github.com/telefonicaid/fiware-testbed-deploy/

Top_

Deletion of Unaccepted Terms & Conditions users
===============================================

You can find here details about `Deletion of users that does not accept new Terms and Conditions <scripts/unacceptedTermsAndConditions>`_

Top_


Support
=======

Ask your thorough programming questions using `stackoverflow`_ and your general questions on `FIWARE Q&A`_.
In both cases please use the tag *fiware-skuld*.

Top_


License
=======

\(c) 2015 Telefónica I+D, Apache License 2.0

.. IMAGES

.. |Build Status| image:: https://travis-ci.org/telefonicaid/fiware-skuld.svg?branch=develop
   :target: https://travis-ci.org/telefonicaid/fiware-skuld
   :alt: Build status
.. |StackOverflow| image:: https://img.shields.io/badge/support-sof-yellowgreen.svg
   :target: https://stackoverflow.com/questions/tagged/fiware-skuld
   :alt: Help? Ask questions
.. |Coveralls| image:: https://coveralls.io/repos/telefonicaid/fiware-skuld/badge.svg?branch=develop&service=github
   :target: https://coveralls.io/github/telefonicaid/fiware-skuld?branch=develop
   :alt: Unit tests coverage
.. |License Badge| image:: https://img.shields.io/badge/license-Apache_2.0-blue.svg
   :target: LICENSE
   :alt: Apache 2.0

.. REFERENCES

.. _FIWARE: http://www.fiware.org/
.. _stackoverflow: http://stackoverflow.com/questions/ask
.. _`FIWARE Q&A`: https://ask.fiware.org
.. _SkuldForAll: ./SkuldForAll/README.rst
.. _impersonate.sh: ./fiwareskuld/on_keystone/README.rst
.. _NewFiwareKeystone: https://github.com/jicarretero/NewFiwareKeystone

