#!/bin/bash

# This script needs 2 files:

# users_to_delete_phase3.txt
# This file is made of lines containing <user_id>,<email>

file=$1
[ -z $file ] && exit 1

for user in $(cat $file); do
  trust_id=$(ssh -p 8022 root@130.206.84.8 "~/impersonate.sh $user")
  mail=$(awk -F ',' "/$user,/ {print \$2}" users_to_delete_phase3.txt)
  echo $mail,$trust_id,$user
done
