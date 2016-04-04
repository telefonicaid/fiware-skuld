FROM ubuntu
RUN apt-get update && sudo apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb mysql-server
RUN git clone https://github.com/telefonicaid/fiware-skuld/ /opt/fiware-skuld/
WORKDIR /opt/fiware-skuld/
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
RUN python setup.py install

WORKDIR /opt/fiware-skuld/tests/acceptance/
RUN pip install -r requirements.txt
COPY configuration.py common/configuration.py
COPY start.sh .
CMD ./start.sh
