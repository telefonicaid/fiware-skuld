echo $OS_USERNAME
echo $OS_TENANT_NAME
echo $OS_PASSWORD
echo $OS_REGION_NAME
echo $OS_AUTH_URL
echo $BOOKED_IP

tests/install_testbed/launch_vm_phonehome.py >cmd.log 2>&1
cat cmd.log
export ip1=`grep "Region1 IP:" cmd.log | awk '{print $4}'`
export region1=`grep "Region1 IP:" cmd.log | awk '{print $3}'`
export region2=`grep "Region2 IP:" cmd.log | awk '{print $3}'`
export uuid1=`grep "$region1: VM with UUID" cmd.log | awk '{print $5}'`
if [ -z "${ip1}" ]; then
    echo "Error to deploy the VM or obtain the IP"
    if [ -z "${uuid1}" ]; then
        exit;
    fi
    nova delete $uuid1
    exit;
fi
echo "waiting for vm"
while ! nc -z $ip1 22; do sleep 8; done
