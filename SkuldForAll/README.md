# SkuldForAll
[![License badge](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction
These are a set of Scripts thought to replace phase_0 of [Skuld](../README.rst) 

This means that these scripts are thought to find out the users that should be removed from a region after their account has been expired.

## Prerequistes
You'll need **python-openstackclient** installed so the scripts can properly work. The script uses python 2.7. It is also highly recommended to install [jq](https://stedolan.github.io/jq/)

It is interesting to configure the file **fiware-users.ini** whith the appropiate values for the region before running the scripts.

## Description
These are 3 scripts thought to work one after the other. 

### interesting_info.py
The script **interesting_info.py** will get a lot of information from a FIWARE Openstack node, including users, projects, role_assignments, etc. So an administrator can see a lot of information in a json output.

The output of the file is quite long and it takes some tome to finish, so it is interesting to store that information somewhere to be analized off line. The script takes some time to finish. The way to use this script is running:

    ./interesting_info.py > /tmp/all.json

The file /tmp/all.json can be analyzed later in order to extract the information you need.

### get_outdate_people.py
There is another script named **get_outdate_people.py**. It will read the file /tmp/all.json and will display the output of the users assigned to projects in a region.

You can change the following lines in order to configure your script:

    REGION = 'Noida'
    JSON_DATA_FILE = '/tmp/all.json'

The first line shows the region you want to query and the second is the json file you want to process.

The output of the file is a set of lines like these, the fields are separated by a white space:

    <type> <user_id> <start_date> <duration> <days_expired> <email> <projects> 


- *type* -- Can be T(trial) or C(community)
- *user_id* -- The user id in Keystone
- *start_date* -- The starting date of the Community or Trial account.
- *duration*  -- The duration of the account. Usually 270 days for community and 15 days for trials.
- *days_expired* -- Days the project has been expired. A negative value means it has not expired yet
- *email*  -- User email
- *projects* -- Number of projects the user belongs to.


There's a second way to use this script. This is adding the parameter **json** as a first parameter of the script. This will produce a json output where you can get a lot of information about users and projects in a more convenient way than the previous script. At least in order to analize it through projects and users.

A typical way to use the script is:
    ./get_outdate_people.py json > /tmp/outdated_people.json

### skulded.py
The script **skulded.py** will read the file /tmp/outdate_people.json and will analyze what projects can be deleted in the region selected.

At the beginning of the Script, there are a few global variables wich will help to configure the script:

    REGION = 'Spain2'
    JSON_DATA_FILE = '/tmp/outdated_people.json'
    WHITE_LIST = 'whitelist.txt'

- The REGION (wich should be the same it was in Script interesting_info.py
- JSON_DATA_FILE -- which should be the output of the script get_outdate_people.py
- WHITE_LIST -- Which is a file made of regular expressions in order to prevent users to be "removable"

As an example of WHITE_LIST file to prevent deleting people of domains "@fiware.org", "@example.com" and "john.doe@somewhere.is":

    .*@fiware.org$
    .*@example.com$
    john.doe@somewhere.is$

We can redirect users to some json file

    ./skulded.py > /tmp/skulded.json

From that file, we can get the users we want to remove or anything just analyzing the json file. Here are a few examples:

- **Select Trial users to be removed**

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Trial" and .enabled==true) | .name' /tmp/skulded.json | sort > sorted_trial_users.txt

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Trial") | .id + "," + .name' ./skulded.json > users_to_delete_phase3.txt


- **Select Community users to be removed**

    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Community" and .enabled==true) | .name' /tmp/skulded.json| sort > sorted_community_users.txt


    jq -r '.users | to_entries[].value | select(.removable==true and .type=="Community") | .id + "," + .name' ./skulded.json > users_to_delete_phase3.txt
