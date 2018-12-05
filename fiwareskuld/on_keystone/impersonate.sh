#!/bin/bash 

# The 1st parameter is the user which is going to be a trusted_user. It should not be Admin.

user=$1
force_project_id=$2


if [ -z $user ]; then
    echo User must be the 1st parameter
    exit 1
fi

# The script is thought to be run in the keystone database host
# Change these variables....
keystone_user=keystone
keystone_password=keystone
keystone_database=keystone
trustee_id=jose-ignacio

# Nothing left to change....
impersonation=1


trust_id=$(uuidgen | sed 's|-||g')


data=($(openstack user show ${user} | awk '/cloud_project_id/ {cpid=$4}; / id / {user_id=$4} ; END {print user_id, cpid}'))
#data[0] - user_id
#data[1] - cloud_project_id

if [ -z $data ] ; then
    echo Openstack error 
    exit 1
fi

user_id=${data[0]}
cloud_project_id=${data[1]}

[ ! -z $force_project_id ] && cloud_project_id=$force_project_id

expires_at=$(date --date="tomorrow" +"%Y-%m-%d %H:%M:%S")

role_id=$(openstack role assignment list -f value -c Role --project  ${cloud_project_id} --user ${user_id} | tail -1)

if [ -z $role_id ] ; then
    echo "Role not found error"
    exit 1
fi
extra="{\"allow_redelegation\": true, \"roles\": [{\"id\": \"${role_id}\"}]}"

mysql -u ${keystone_user} -p${keystone_password} ${keystone_database} -e "insert into trust (id, trustor_user_id, trustee_user_id, project_id, impersonation, expires_at, extra) values (\"${trust_id}\", \"${user_id}\",\"${trustee_id}\",\"${cloud_project_id}\",1,\"${expires_at}\",'${extra}') ; insert into trust_role(trust_id, role_id) values (\"${trust_id}\",\"${role_id}\")" 2>/dev/null


echo $trust_id

