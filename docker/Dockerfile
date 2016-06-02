FROM ubuntu
RUN apt-get update && apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb 
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install  mysql-server
RUN pip install --upgrade pip
RUN pip install git+https://github.com/telefonicaid/fiware-skuld@develop
RUN git clone https://github.com/telefonicaid/fiware-skuld/ /opt/fiware-skuld/
WORKDIR /opt/fiware-skuld/
COPY settings.py conf/settings.py
WORKDIR /opt/fiware-skuld/tests/acceptance/
RUN pip install -r requirements.txt
RUN mkdir testreport
COPY configuration.py commons/configuration.py
COPY start.sh .
CMD ./start.sh
