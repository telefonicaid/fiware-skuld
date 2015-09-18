=========================================
FIWARE Delete Unaccepted Terms&Conditions
=========================================

.. contents:: :local:

Introduction
============

This Script is writen in order to suggest what VMs in FIWARE Lab should be deleted because users 
have not accepted the `FIWARE LAB Terms and Conditions`_. The results of this script must be taken 
as a suggestion being a concern of each node administrator to decide what to do with the suggestions.

The script uses 2 temporary files:

- /tmp/accepted_list.txt  -- The file containing the user names who have accepted
- /tmp/vm_file.txt  -- The list of the instances in the node

The scripts produces 4 result files:

- /tmp/2delete.txt  -- This is a result file. A "script like" file of nova-delete suggesting the 
  commands to be executed.
- /tmp/2keep.txt   -- This is another result file of images to be kept.
- /tmp/2check.txt  -- This file is to manually check what to do with a VM.
- /tmp/ips2delete.txt -- This another "script like" file suggesting the commands to be executed to 
  delete floating IPs of users who have not accepted.
- /tmp/2workon.txt  -- This is a file formated with "user tenant" in each line; You can surely find 
  things to be cleaned belonging to this user after the deletion of VMs and floating-ips is done.

Before running the Script you must set the openstack variables, or exec your own "keystonerc" file:

.. code::

    export OS_AUTH_URL=xxx
    export OS_USERNAME=xxx
    export OS_PASSWORD=xxx
    export OS_TENANT_NAME=xxx
    export OS_REGION_NAME=xxx


What it'll be suggested to delete
=================================

Any user who has not explicitly accepted the new Terms and conditions and who signed up in the system 
before 20th February of 2015. Users who signed up after that date accepted the terms and conditions at 
Sign up time.


What it'll be suggested to check
================================

- Organizations (Groups)
- New Users (Signed up after 20th February 2015)

What it'll be suggested to keep
===============================

- Users who explicitly accepted the new Terms and Conditions.

Known issues
============

- Please, be aware that this script doesn't seem to work with organizations. If a VM belongs to an organization, 
  it is writen a "log line" in file /tmp/2check.txt -- This must be tested manually.

- "nova list" only return 1000 results. If the amount of instances is bigger than that, the script might not 
  completely work. It might be useful to be executed serveral times after the deletions.

- This is not ready yet to clean and delete networks and routers for users.

- Maybe, "nova delete xxx" doesn't work in some places and they need to do some "nova shutdown" before running 
  "nova delete". As a workaround, you can create a "shutdown script" from the "delete script" just this way:

.. code::

   sed "s|^nova delete|nova shutdown|g" /tmp/2delete.txt > /tmp/2shutdown.txt

- After the deletion, you may consider cleaning other things (networks, routers, private images, cinder volumes, 
  Objects stored, etc) belonging to this user. You can check user/tenants to be cleand in file /tmp/2workon.txt




.. REFERENCES

.. _FIWARE LAB Terms and Conditions: https://forge.fiware.org/plugins/mediawiki/wiki/fiware/index.php/FIWARE_LAB_Terms_and_Conditions
