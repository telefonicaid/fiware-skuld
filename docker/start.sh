sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" common/configuration.py
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" common/configuration.py
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" common/configuration.py
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" common/configuration.py

export PYTHONPATH=../..
behave features/ --tags ~@skip --junit --junit-directory testreport
