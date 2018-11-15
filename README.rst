.. _Top:

===========================================
FIWARE Componets: Installation in Openshift
===========================================

.. contents:: :local:

Introduction
============
There are a few FIWARE_ components which has been successfully installed under OpenShift.

* Orion
* IoT Agents
* Cygnus
* STH-Commet

Some aditional components are needed in order to make things work:

* MongoDB
* Mosquitto Server
* ...

Helper Container Installation
=============================
MongoDB
-------
It is easy to deploy a Mongo Database in order to work with it in the deployment

.. code:: bash

 oc new-app mongo:3.6 --name mongo

Mysql
-----
To deploy a MySQL databas we can proceed this way:

.. code:: bash
  
   oc new-app centos/mysql-57-centos7 --name mysql \
   -e MYSQL_ROOT_PASSWORD=root

MySQL is going to be used in Cygnus, so, just using the root password Cygnus will be able to create the database by itself.

Orion Context Broker
====================
.. code:: bash

 oc new-app  fiware/orion:1.7.0 --name orion -o yaml > orion.yaml

We should edit the orion.yaml file in order to add the parameter "-dbhost mongo" to the entrypoint as Orion_ starts, so Orion can connect to the database.

.. code:: yaml
   :emphasize-lines: 4-9

 .....
   kind: DeploymentConfig
 .....
       containers:
        - image: fiware/orion:1.7.0
          name: orion
          args:
            - -dbhost
            - mongo
          ports:
          - containerPort: 1026
            protocol: TCP
          resources: {}
 .....

Once changed the file, we can deploy Orion_ Context Broker this way:
 .. code:: bash

  oc create -f orion.yaml

Cygnus
======
The Cygnus image has been created using another image. The repository is **jicarretero/cygnus-ngsi-ff-jicg:1.8.0**. There are documented 2 ways to use Cygnus here. Using MySQL and using MongoDB.

The image was created because there was a strong version requisite: Cygnus 1.8.0.

Cygnus-mysql
------------
In order to create that cygnus:

.. code:: bash

  oc new-app jicarretero/cygnus-ngsi-ff-jicg:1.8.0 --name cygnus-mysql \
  -e CYGNUS_MYSQL_HOST=mysql -e CYGNUS_MYSQL_PORT=3306 -e CYGNUS_MYSQL_USER=root -e CYGNUS_MYSQL_PASS=root \
  -o yaml > new_cygnus_mysql.yaml

We also need to create a config Map so the directory where the configuration data is stored can be upgraded. Before creating the configMag, we should edit the file **agent.conf** so we can set the properties of or MySQL database. In example, as created previously.

.. code:: bash

 oc create configmap cygnus-agent-config-mysql --from-file=conf.mysql/


Once the config map and the yaml is created, we edit the file in order to use the config map recently created

.. code:: yaml

   ....
   kind: DeploymentConfig
   ....
     spec
     ....
       template
         ....
         spec
           containers:
           - image: jicarretero/cygnus-ngsi-ff-jicg:1.8.0
             name: cygnus-mysql
             ports:
             - containerPort: 5050
               protocol: TCP
             - containerPort: 8081
               protocol: TCP
             resources: {}
             volumeMounts:
               - name: cygnus-agent-config-mysql
                 mountPath: /opt/apache-flume/conf
           volumes:
               - name: cygnus-agent-config-mysql
                 configMap:
                   name: cygnus-agent-config-mysql
     ......

Cygnus Mongo
-------------
This basically the same as Cygnus-mysql but using Mongodb variables.

.. code:: bash

 oc new-app jicarretero/cygnus-ngsi-ff-jicg:1.8.0 --name cygnus-mongo \
 -e CYGNUS_MONGO_HOSTS=mongo -e CYGNUS_MONGO_USER="" -e CYGNUS_MONGO_PASS="" -o yaml > new_cygnus_mongo.yaml
  

We also need to create a config Map so the directory where the configuration data is stored can be upgraded. Before creating the configMag, we should edit the file **agent.conf** so we can set the properties of or MySQL database. In example, as created previously.

.. code:: bash

 oc create configmap cygnus-agent-config-mongo --from-file=conf/


Once the config map and the yaml is created, we edit the file in order to use the config map recently created

.. code:: yaml

   ....
   kind: DeploymentConfig
   ....
     spec
     ....
       template
         ....
         spec
           containers:
           - image: jicarretero/cygnus-ngsi-ff-jicg:1.8.0
             name: cygnus-mysql
             ports:
             - containerPort: 5050
               protocol: TCP
             - containerPort: 8081
               protocol: TCP
             resources: {}
             volumeMounts:
               - name: cygnus-agent-config-mongo
                 mountPath: /opt/apache-flume/conf
           volumes:
               - name: cygnus-agent-config-mongo
                 configMap:
                   name: cygnus-agent-config-mongo
     ......
     
We will also need to check the values of the variables CYGNUS_MONGO_USER and CYGNUS_MONGO_PASS which will have an empty "value" for those variables. That prevent things from working.
     

.. _FIWARE: http://www.fiware.org/
.. _Orion: https://github.com/telefonicaid/fiware-orion
