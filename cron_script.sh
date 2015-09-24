#!/bin/bash

cd $(dirname $0)

. deleteENV/bin/activate

# generate lists
./phase0_generateuserlist_alt.py

# notify users next to expire
./phase0b_notify_users.py

# change type of expired users
./phase0c_change_category.py

# stop servers of expired users
if [ ! -f users_to_delete_phase3.txt ] ; then
./phase1_generate_trust_ids.py
./phase2_stopvms.py
rm users_trusted_ids.txt
fi

# delete resources of users who expired days ago (i.e. accounts that were
# processed by the phase2_stopvms some days ago)
if [ -f users_to_delete_phase3.txt ] ; then
./phase1_generate_trust_ids.py users_to_delete_phase3.txt
rm users_to_delete_phase3.txt
./phase3_delete.py
rm users_trusted_ids.txt
fi
