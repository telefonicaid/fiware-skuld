tests/install_testbed/launch_vm.py >cmd.log 2>&1
cat cmd.log
export ip=`grep "Assigning floating IP" cmd.log | awk '{print $4}'`
export uuid=`grep UUID cmd.log | awk '{print $5}'`
echo $ip
echo $uuid
if [ -z "${ip}" ]; then
    echo "VAR is unset or set to the empty string"
    nova delete $uuid
    exit;
fi
echo "waiting"
while ! nc -z $ip 9696; do sleep 8; done
echo "console log"
sleep 20
nova console-log $uuid > logvm
export region=`grep OS_REGION_NAME logvm | sed  's/export OS_REGION_NAME=//g' | sed 's/OS_REGION_NAME=//g' | awk 'NR==1{print $2}'`
export password=`grep OS_PASSWORD logvm | sed  's/export OS_PASSWORD=//g' | sed 's/OS_PASSWORD=//g' | awk 'NR==1{print $2}'`
export username=`grep OS_USERNAME logvm | sed  's/export OS_USERNAME=//g' | sed 's/OS_USERNAME=//g' | awk 'NR==1{print $2}'`
echo "export OS_USERNAME=$username
export OS_PASSWORD=$password
export OS_TENANT_NAME=$username
export OS_REGION_NAME=$region
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3
export OS_AUTH_URL=http://$ip:5000/v3" >> credentials

cat credentials
. credentials
nova list
neutron net-list
keystone user-list
sleep 10000