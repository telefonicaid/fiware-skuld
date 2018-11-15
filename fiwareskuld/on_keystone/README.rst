=====================
Script impersonate.sh
=====================

This script takes the user (Trustor User) as parameter and creates a trust_id for the user shown in the script:

.. code:: bash

    trustee_id=jose-ignacio

This script is invoked by the new phase1 procedure. The script is installed where it can
connect the Keystone Database in order to force a *Trust* from the Trustor (the user whose 
resources are going to be removed) and the Trustee (the Non Admin user who is going to remove
the resources).

The way to use the script is:

.. code:: bash

   impersonate.sh <email> [<force_project_id>]

And the script will create a *Trust* for the user ``trustee_id`` (in the script code) and for
the user identified by the email and for a project it detects (the first one detected). However, the project_id can be forced with a second optinal parameter.

