tests/install_testbed/deploytwotestbeds.py >cmd.log 2>&1
cat cmd.log
export ip1=`grep "Region1 IP:" cmd.log | awk '{print $4}'`
export ip2=`grep "Region2 IP:" cmd.log | awk '{print $4}'`
export region1=`grep "Region1 IP:" cmd.log | awk '{print $3}'`
export region2=`grep "Region2 IP:" cmd.log | awk '{print $3}'`
export uuid1=`grep "$region1: VM with UUID" cmd.log | awk '{print $5}'`
export uuid2=`grep "$region2: VM with UUID" cmd.log | awk '{print $5}'`
if [ -z "${ip1}" ]; then
    echo "Error to deploy the VM or obtain the IP"
    if [ -z "${uuid1}" ]; then
        exit;
    fi
    nova delete $uuid1
    exit;
fi
if [ -z "${ip2}" ]; then
    echo "Error to deploy the VM or obtain the IP"
    if [ -z "${uuid2}" ]; then
        exit;
    fi
    nova delete $uuid2
    exit;
fi
echo "waiting for keystone"
while ! nc -z $ip1 5000; do sleep 8; done
echo "waiting for testbed one"
while ! nc -z $ip1 9696; do sleep 8; done
echo "waiting for testbed two"
while ! nc -z $ip2 9696; do sleep 8; done

echo "console log"
sleep 20
nova console-log $uuid1 > logvm
nova console-log $uuid2 > logvm2
export region=`grep OS_REGION_NAME logvm | sed  's/export OS_REGION_NAME=//g' | sed 's/OS_REGION_NAME=//g' | awk 'NR==1{print $2}'`
export password=`grep OS_PASSWORD logvm | sed  's/export OS_PASSWORD=//g' | sed 's/OS_PASSWORD=//g' | awk 'NR==1{print $2}'`
export username=`grep OS_USERNAME logvm | sed  's/export OS_USERNAME=//g' | sed 's/OS_USERNAME=//g' | awk 'NR==1{print $2}'`
echo "export OS_USERNAME=$username
export OS_PASSWORD=$password
export OS_TENANT_NAME=$username
export OS_REGION_NAME=$region
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3
export OS_AUTH_URL=http://$ip1:5000/v3" >> credentials


cat credentials
unset OS_USERNAME
export OS_USERNAME=$username
unset OS_PASSWORD
export OS_PASSWORD=$password
unset OS_TENANT_NAME
export OS_TENANT_NAME=$username
unset OS_REGION_NAME
export OS_REGION_NAME=$region
unset OS_PROJECT_DOMAIN_ID
unset OS_PROJECT_DOMAIN_NAME
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3
unset OS_AUTH_URL
export OS_AUTH_URL=http://$ip1:5000/v3/
export OS_AUTH_URL_V2=http://$ip1:5000/v2.0/
nova list
neutron net-list
openstack user list

export region=`grep OS_REGION_NAME logvm2 | sed  's/export OS_REGION_NAME=//g' | sed 's/OS_REGION_NAME=//g' | awk 'NR==1{print $2}'`
export password=`grep OS_PASSWORD logvm2 | sed  's/export OS_PASSWORD=//g' | sed 's/OS_PASSWORD=//g' | awk 'NR==1{print $2}'`
export username=`grep OS_USERNAME logvm2 | sed  's/export OS_USERNAME=//g' | sed 's/OS_USERNAME=//g' | awk 'NR==1{print $2}'`
echo "export OS_USERNAME=$username
export OS_PASSWORD=$password
export OS_TENANT_NAME=$username
export OS_REGION_NAME=$region
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3
export OS_AUTH_URL=http://$ip1:5000/v3" >> credentials

cat credentials
unset OS_USERNAME
export OS_USERNAME=$username
unset OS_PASSWORD
export OS_PASSWORD=$password
unset OS_TENANT_NAME
export OS_TENANT_NAME=$username
unset OS_REGION_NAME
export OS_REGION_NAME=$region
unset OS_PROJECT_DOMAIN_ID
unset OS_PROJECT_DOMAIN_NAME
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3
unset OS_AUTH_URL
export OS_AUTH_URL=http://$ip1:5000/v3/
export OS_AUTH_URL_V2=http://$ip1:5000/v2.0/
nova list
neutron net-list
openstack user list

