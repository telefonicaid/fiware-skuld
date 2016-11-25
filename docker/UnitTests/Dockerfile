FROM ubuntu
ENV GIT_REV story/CLAUDIA-6188_community_users
RUN apt-get update &&  apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb 
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install  mysql-server
RUN git clone https://github.com/telefonicaid/fiware-skuld/ /opt/fiware-skuld/
WORKDIR /opt/fiware-skuld/
RUN git checkout ${GIT_REV}
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
RUN python setup.py install
RUN mkdir coverage
RUN mkdir test_results
CMD nosetests --with-coverage --cover-package=./ --cover-xml --cover-xml-file=coverage/coverage.xml --with-xunit --xunit-file=test_results/TEST-nosetests.xml --exe
