FROM ubuntu
RUN apt-get update && sudo apt-get -y install python-pip python-dev \
  libmysqlclient-dev libpq-dev \
  libxml2-dev libxslt1-dev git \
  libffi-dev zip python-mysqldb mysql-server
RUN git clone https://github.com/telefonicaid/fiware-skuld/ /home/ubuntu/fiware-skuld/
WORKDIR /home/ubuntu/fiware-skuld/
RUN git checkout docker
RUN git branch
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
RUN python setup.py install
RUN mkdir /root/.ssh
COPY start.sh /home/ubuntu/fiware-skuld/start.sh
CMD ./start.sh

