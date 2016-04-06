sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" commons/configuration.py
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" commons/configuration.py
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" commons/configuration.py
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" commons/configuration.py
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" commons/configuration.py

export PYTHONPATH=../..
behave features/ --tags ~@skip --junit --junit-directory testreport
sleep 12000
