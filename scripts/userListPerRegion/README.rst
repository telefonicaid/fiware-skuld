.. _Top:

Skuld - Get the list of users working in a region
*************************************************

.. contents:: :local:

Overview
========

This script file recovers the information of the different users that can be using
the resources in a specific region. It is important that the execution of the scripts
will be done using the correct administrator account for the region that you want to
know your data.

Build and Install
=================

Requirements
------------

The following software must be installed (e.g. using apt-get on Debian and Ubuntu,
or with yum in CentOS):

- Python 2.7
- pip
- virtualenv

Top_

Installation
------------

The recommend installation method is using a virtualenv. Actually, the installation
process is only about the python dependencies, because the python code do not need
installation.

1) Create a virtualenv 'scriptsUser' invoking *virtualenv scriptsUser*
2) Activate the virtualenv with *source scriptsUser/bin/activate*
3) Install the requirements running *pip install -r requirements.txt*

Now the system is ready to use. For future sessions, only the step2 is required.

Top_

Running
=======

To run the process just follow the indications provided by the client component.
Just execute the following command:

.. code::

     $ ./users.py -h

To see the help information about the use of this script, like the following:

.. code::
    Get the users list of a specific FIWARE Lab region.

    Usage:
      users --user=<username> --pass=<password> --region=<region> [--out=<filename>]
      users -h | --help
      users -v | --version

    Options:
      -h --help           Show this screen.
      -v --version        Show version.
      -o --out=<filename> Store the information if the file <filename>.
      --user=<username>   Admin user that request the data.
      --pass=<password>   Admin password of the user.
      --region=<region>   Region name that we want to recover the information.

A typical execution of this script could be:

.. code::
    ./users.py --user <Admin user from Trento> --pass <Password> --region Trento --out a.out

Keep in mind that the user should be the corresponding administrator of the region from
which you want to know the list of users that can use their resources. This value is
unique and identified in the Keystone for all the regions.

Top_


License
=======

\(c) 2015 Telefónica I+D, Apache License 2.0

Top_
