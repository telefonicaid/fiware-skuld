sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" commons/configuration.py
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" commons/configuration.py
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" commons/configuration.py
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" commons/configuration.py
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" commons/configuration.py
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" ./../../fiwareskuld/conf/settings.py
export OS_REGION_NAME=$Region1
export  OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export  OS_AUTH_URL=http://$KEYSTONE_IP:5000/v2.0
export PYTHONPATH=../..
behave features/ --tags ~@skip --junit --junit-directory testreport
