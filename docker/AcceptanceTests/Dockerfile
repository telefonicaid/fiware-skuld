FROM ubuntu
ENV GIT_REV develop
RUN apt-get update && apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb 
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install  mysql-server
RUN pip install --upgrade pip; pip install git+https://github.com/telefonicaid/fiware-skuld@${GIT_REV}
RUN git clone https://github.com/telefonicaid/fiware-skuld/ /opt/fiware-skuld/
WORKDIR /opt/fiware-skuld
RUN git checkout ${GIT_REV}
WORKDIR /opt/fiware-skuld/tests/acceptance/
RUN pip install -r requirements.txt
COPY start.sh .
CMD ./start.sh
